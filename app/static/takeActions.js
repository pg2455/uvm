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
  stumble = false
  var x = 0;
  if(action.toLowerCase()!='nothing'){
    controller('stop',action)
    console.log('Taking action', action)
    $.blockUI({
      message : $('#question').prepend('<h1>'+action+'</h1>'),
      timeout:5000,
      onUnblock: function(){
        if(x>0){
          return;
        }
        x++
        reaction = 'down'
        controller('start',reaction)
        console.log('normal unblocking')
        $('#question h1').first().remove();
        // msgIdChanged = true
      }
    });

    $('#yes').click(function() { // skip
        if(x>0){
          return;
        }

        x++;
        reaction = 'down'
        controller('start',reaction)
        $.unblockUI(); // this goes to above onUnblock control
        $('#question h1').first().remove();

    });

    $("#no").click(function(){ // end session
      if(x>0){
        return;
      }
      console.log(x)
      x++;
      reaction = 'dead'
      controller('start',reaction)
      $.unblockUI();
      $('#question h1').first().remove();
    })

    $("#random").click(function(){ // stumble upon
      if(x>0){
        return;
      }
      x++;
      url = stumbleUpon()
      URL = url
      reaction = 'right'
      controller('start',reaction)
      $.unblockUI();
      $('#question h1').first().remove();
      // if(msgIdChanged == false){
      //   $('#question h1').first().remove();
      // }
      // msgIdChanged = false
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
