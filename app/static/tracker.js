interval = 1000; // ms
// track clicks on link
function trackClicks(){
  $('a').click( function() {
    saveTime();
    // $.post('http://0.0.0.0:9090/recordClick', {data:$(this).attr('src')}, function (){});
    console.log(sessionTimes);
  });
}

// start your session
function startSession() {
  startTime = (new Date()).getTime();
  sessionTimes = [];
  sessionStartTime =  (new Date()).getTime();

  //plotting variables
  chart_pv =[], chart_pr=[],chart_pp=[];
  value_pv =[], value_pr=[], value_pp=[];
  total_value = [];

  // cost constants
  Cv = 2; // cents
  Cp = 33.33; //cents
  rppv = 10; //cents
  future_impact = 1.01 // future impact

  // regression constants
  beta_atsop = 2/mean_atsop;
  beta_sd = 0.1/mean_sd;
  video_constant = 0;
  recommendation_constant = 1.044;

  beta_subscription_atsop = 1/catsop;
  beta_subscription_pv = 0.1/(visits * mean_sd);
  subscription_constant = 4;
}

// store time spent
function saveTime(){
  endTime = (new Date()).getTime();
  elapsedTime = endTime - startTime;  // in ms
  sessionTimes.push(elapsedTime);
  startTime = (new Date()).getTime();
}

// unload event
window.onbeforeunload = function() {
  saveTime();
  $.ajax({
   contentType: 'application/json; charset=UTF-8',
   url: '/feedback',
   data: JSON.stringify({times: sessionTimes}),
   type: 'POST',
   success: function() {alert("feedback sent")},
   dataType:"json",
 });
};

function cutArray(an_array){
  if (an_array.length <=10){
    return an_array;
  }else{
    console.log(an_array.splice(-10))

    return an_array.splice(-10);
  }
}

// call this function every second to calculate the prob of video and links
window.setInterval(function(){
  // calculate probabilities of user's reaction
  time_diff = (new Date()).getTime() - sessionStartTime;

  slacr = sessionTimes.slice(-1)/time_diff;
  lacr = ((new Date()).getTime() - startTime)/time_diff;
  sd = sessionTimes.length + 1;
  console.log("interval",sd, sessionTimes.slice(-1), time_diff, lacr*time_diff)
  cum_atsop = catsop + time_diff

  pv = 1-1/(1+Math.exp(-(beta_atsop*time_diff - video_constant)))
  chart_pv.push({y:pv})

  if (sd ==1){
    pr  = 1- Math.exp(beta_sd*sd + beta_atsop*time_diff- recommendation_constant)
  }else{
    pr = getPr(lacr,slacr, sd)
  }
  // pr  = 1- Math.exp(beta_sd*sd + beta_atsop*time_diff- recommendation_constant)

  chart_pr.push({y:pr})

  pp = 1/(1+Math.exp(-(beta_subscription_atsop*cum_atsop + beta_subscription_pv*(visits*mean_sd + sd) - subscription_constant )));
  chart_pp.push({y:pp})


  // use above to recommend action to publisher
  total  =  pv + pr +pp
  av = pv/total;
  ar = pr/total;
  ap = pp/total;

  // expected values from above probabilistic actions
  Cr = (rppv + ap*pp*Cp + av*Cv)/(1-ar*pr + pr*future_impact*(ap*(1-pp) + av*(1-pv)))
  _value_pr = pr*Cr
  _value_pv = -(1-pv)*pr*Cr + Cv
  _value_pp = -(1-pp)*pr*Cr + pp*Cp
  value_pr.push({y:_value_pr}); value_pv.push({y:_value_pv}); value_pp.push({y:_value_pp});


  _total_value = av*_value_pv + ar*_value_pr + ap*_value_pp;
  total_value.push({y:_total_value});

  //
  // chart_pv = cutArray(chart_pv); chart_pr= cutArray(chart_pr); chart_pp = cutArray(chart_pp)
  // value_pv= cutArray(value_pv); value_pr = cutArray(value_pr); value_pp = cutArray(value_pp)
  // total_value = cutArray(total_value)


  // console.log(_total_value)

  //plot above values
  chart1.options.data[0].dataPoints = total_value;
  chart1.options.data[1].dataPoints = value_pv;
  chart1.options.data[2].dataPoints = value_pr;
  chart1.options.data[3].dataPoints = value_pp;

  chart1.render();

  chart2.options.data[0].dataPoints = chart_pv;
  chart2.options.data[1].dataPoints = chart_pr;
  chart2.options.data[2].dataPoints = chart_pp;

  chart2.render();


}, interval);
