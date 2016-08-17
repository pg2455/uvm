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
continueFurther = true;
atsop_count = 0;
current_cell =1;
prev_cell = current_cell;

function sendFeedback(current_cell, prev_cell, action, reaction){
  $.ajax({
    url:'http://0.0.0.0:9090/updates',
    contentType:"application/json",
    data:JSON.stringify({"prev_state":prev_cell, "next_state":current_cell, "action":action, "reaction":reaction}),
    type:"POST",
    success: function(){
      console.log("ssd")
    }
  })
}

function takeAction(){
  random_number = Math.random();
  ActionTaken ="Nothing"
}

// call this function every second to calculate the prob of video and links
window.setInterval(function(){
    takeAction();
    if(ActionTaken == 'Nothing'){

        atsop_count +=1
        current_cell = (SD-1)*MAX_ATSOP_ROWS + Math.ceil(atsop_count/ATSOP_GAP)
        console.log(atsop_count, current_cell, prev_cell, SD);
        if(current_cell != prev_cell){
          action = ActionTaken;
          sd_diff = SD - prev_sd;

          if(sd_diff>0){
            for(x=0; x< sd_diff; x++ ){
              reaction = 'right';
              sendFeedback(current_cell, prev_cell+ (x *MAX_ATSOP_ROWS), action, reaction)
            };
          }else {
            reaction="down";
            sendFeedback(current_cell, prev_cell, action, reaction)
          }
        }
        prev_cell = current_cell


      prev_sd = SD;
  }
}, interval);
