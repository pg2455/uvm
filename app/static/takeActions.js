
var screenBlocked=false;

// Publisher takes actions independednt
function chooseAction(prob){
  rand = Math.random();
  cum_prob = 0
  for(i in prob){
    cum_prob += prob[i]
    if(rand < cum_prob){
      return i
    }
  }
}



// takes actions, observes reaction, sends feedback to stateTracker
function takeAction(action){

  // console.log("Take Action", action, CURRENT_CELL)

  if(action.toLowerCase()!='nothing'){
    takingAction = true
    // send this feedback to central function
    at_atsop = atsop
    screenBlocked = true;
    $.blockUI({
      message : $('#question').prepend('<h1>'+action+'</h1>'),
      timeout:4000,
      onUnblock: function(){
        screenBlocked =false;
        reaction = 'down'
        recordFeedback(CURRENT_CELL, action, reaction)
        $('#question h1').first().remove();
        takingAction = false;
      }
    });

    $('#yes').click(function() {
        $.unblockUI();
        screenBlocked = false;
        reaction = 'down';
        recordFeedback(CURRENT_CELL, action, reaction)
        takingAction=false;
    });

    $("#no").click(function(){
      reaction = 'dead'
      recordFeedback(CURRENT_CELL, action, reaction)
      // window.location.href = "http://0.0.0.0:9090/"
    })
    $('.blockOverlay').attr('title','Click to unblock').click($.unblockUI);
  }else{
    takingAction = false
    screenBlocked = false;
    reaction = 'down'
    recordFeedback(CURRENT_CELL, action, reaction)
  }

}


// unload event
window.onbeforeunload = function() {
  reaction = 'dead'
  recordFeedback(CURRENT_CELL, action, reaction)
};
