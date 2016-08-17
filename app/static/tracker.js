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
  SD=1;
  startTime = (new Date()).getTime();
  sessionTimes = [];
  sessionStartTime =  startTime;
}

// store time spent
function saveTime(){
  endTime = (new Date()).getTime();
  elapsedTime = endTime - startTime;  // in ms
  sessionTimes.push(elapsedTime);
  startTime = endTime;
  SD+=1;

}


function stumbleUpon(){
  list = $('a')
  list = $.each(list,function(e){
    return e.href
  })

}
