function recordFeedback(cell, action, reaction){
  // console.log("record feedback", cell,action, reaction, "end")
  if(reaction == 'down'){
      if(CELL >= MAX_ATSOP_ROWS*SD){
        next_cell = cell
      }else{
        next_cell = cell + 1
        drawDot('top', action)
        FEEDBACK.push({'url':URL,'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})
      }
  }else if(reaction == 'right'){

      if(SD >= MAX_SD_COLS){
        // no reaction
        next_cell = cell
      }else{
        SD += 1
        next_cell = cell + MAX_ATSOP_ROWS
        drawDot('left', action)
        FEEDBACK.push({'url':URL,'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})
      }


  }else{
    next_cell = 1000
    FEEDBACK.push({'url':URL,'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})
    controller('stop','nothing')
    $.ajax({
      url: "http://0.0.0.0:9090/feedback",
      contentType: 'application/json; charset=UTF-8',
      data: JSON.stringify({feedback: FEEDBACK}),
      type:"POST",
    });

    endSession(action)
  }
  CELL = next_cell

}


function activateCounter(){
  var counter = setInterval(function(){


      ATSOP +=ATSOP_GAP
      if (CELL < MAX_ATSOP_ROWS*SD ){
        recordFeedback(CELL,'nothing', 'down') // first execcution takes place after interval.
        // when the atsop_gap time is done it crosses that cell
        // hence record feedback at that instant
      } else{
        // do nothing
      }


      // this will be separate but for demo it is here
      if(CELL%2==0){
        action = chooseAction(ACTION_PROB)
        takeAction(action)
      }

  }, ATSOP_GAP*1000)
  return counter
}

function controller(command, attr){
  // Assumption : stop will occur before start
  if(command=='stop'){
    //attr is action
    clearInterval(counter)
    action = attr

    current_cell = CELL

  } else if(command == 'start'){
    //attr is reaction
    reaction = attr

    recordFeedback(current_cell, action, reaction)
    counter = activateCounter()
  }
}


// for demo
function createGrid(MAX_ATSOP_ROWS, MAX_SD_COLS, WIDTH) {
    var ratioW = MAX_SD_COLS * WIDTH;
        ratioH = MAX_ATSOP_ROWS * WIDTH;

    var parent = $('<div />', {
        class: 'grid',
        width: ratioW,
        height: ratioH
    }).addClass('grid').appendTo('body');

    top_position_dot = parseInt($('#dot').css('top').slice(0,-2))
    right_position_dot = parseInt($('#dot').css('right').slice(0,-2))
    height_dot = parseInt($('#dot').css('height').slice(0,-2))
    $('.grid').css('top',  top_position_dot - WIDTH/2 + height_dot/2 + "px" )
    $('.grid').css('right',  right_position_dot - MAX_SD_COLS*WIDTH + WIDTH/2 + height_dot/2 + "px" )

    for (var i = 0; i < MAX_ATSOP_ROWS; i++) {
        for(var p = 0; p < MAX_SD_COLS; p++){
            $('<div />', {
                width: WIDTH-1,
                height: WIDTH-1
            }).appendTo(parent);
        }
    }
}

function drawDot(attr,label){
  //attr is the dimension to move in

  $('<div/>', {
    class: "path_dots"
  }).addClass("path_dots" +cnt).appendTo('#path')
  $('.path_dots'+cnt).css('top', $("#dot").css('top'))
  $('.path_dots'+cnt).css('left', $("#dot").css('left'))

  if(label.toLowerCase() != 'nothing'){
    $('.path_dots'+cnt).append("<br>"+label.slice(0,1))
  }
  if(attr!='dead'){
    $("#dot").css(attr, "+="+WIDTH+"px");
  }else{
    $("#dot").css('top', '170px')
    $("#dot").css('right', '220px')
  }

  cnt+=1
}


function putLabelsOnGrid(MAX_ATSOP_ROWS, MAX_SD_COLS,ATSOP_GAP, WIDTH){


  _top = parseInt($('#dot').css('top').slice(0,-2)) - WIDTH/2
  _left= parseInt($('#dot').css('left').slice(0,-2))
  _height_dot = parseInt($('#dot').css('height').slice(0,-2))

  for (i=0; i<=MAX_ATSOP_ROWS; i++){
    $('<div/>',{
      class:"label"
    }).addClass('label'+i).appendTo('#labels')

    $('.label'+i).append(ATSOP_GAP*i)
    $('.label'+i).css('top', (_top + WIDTH*i + _height_dot/2 )+"px")
    $('.label'+i).css('left', _left-WIDTH/2 - 25 + "px")
  }

  for (c=1; c<=MAX_SD_COLS; c++){
    $('<div/>',{
      class:"label"
    }).addClass('label'+(c+i)).appendTo('#labels')

    $('.label'+(c+i)).append(c)
    $('.label'+(c+i)).css('top', (_top - 20 +"px"))
    $('.label'+(c+i)).css('left', _left + WIDTH*(c-1) + "px")
  }
}

function putTitlesOnGrid(top_label, side_label){
  _top = parseInt($('#dot').css('top').slice(0,-2))
  _left= parseInt($('#dot').css('left').slice(0,-2))
  _height_dot = parseInt($('#dot').css('height').slice(0,-2))

  $('<div/>',{
    class:"title"
  }).addClass('top_title').appendTo('#titles')

  $('.top_title').append(top_label)
  $('.top_title').css('top', (_top - 80) +"px")
  $('.top_title').css('left', _left + "px")

  $('<div/>',{
    class:"title"
  }).addClass('title_side').appendTo('#titles')

  $('.title_side').append(side_label)
  $('.title_side').css('top', (_top + 100) +"px")
  $('.title_side').css('left', _left - 120 + "px")
}


function endSession(label){

  drawDot('dead',label)
  //notification
  $.blockUI({
    message:"<h3>Sending feedback & Updating backend</h3>",
    fadeIn:700,
    fadeOut:700,
    timeout:2000,
    showOverlay:false,
    centerY:false,
    css:{
      width:'350px',
      top:'10px' ,
      left:'',
      right:'10px' ,
      border:'none',
      padding:'5px',
      backgroundColor: '#000',
    '-webkit-border-radius': '10px',
    '-moz-border-radius': '10px',
    opacity: .6,
    color: '#fff'
    }
  })



  //close after 2 seconds
  setTimeout(function(){
    window.location.href = "http://0.0.0.0:9090/"
  }, 3000)


}

//
// controller('stop', 'video')
// controller('start', 'down')
// controller('stop', 'rec')
// controller('start', 'right')
// controller('stop','paywall')
// controller('start','down')
