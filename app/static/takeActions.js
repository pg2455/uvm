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

  if(action.toLowerCase()!='nothing'){
    controller('stop',action)
    console.log('Taking action', action)
    $.blockUI({
      message : $('#question').prepend('<h1>'+action+'</h1>'),
      timeout:4000,
      onUnblock: function(){
        $('#question h1').first().remove();
        reaction = 'down'
        controller('start',reaction)

      }
    });

    $('#yes').click(function() {
        $.unblockUI(); // this goes to above onUnblock control
    });

    $("#no").click(function(){
      $.unblockUI();
      reaction = 'dead'
      controller('start',reaction)
    })

    $("#random").click(function(){
      reaction = 'right'
      controller('start', reaction)
      url = stumbleUpon()
      URL = url
      $.unblockUI();
      document.getElementById('actualIframe').setAttribute('src', url)
    })

    $('.blockOverlay').attr('title','Click to unblock').click($.unblockUI);
  }

}

// unload event
window.onbeforeunload = function() {
  reaction = 'dead'
  controller('stop','nothing')
  controller('start',reaction) // window will reset to start by itself
};
