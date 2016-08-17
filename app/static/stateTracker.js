FEEDBACK= []
MAX_SD_COLS = 3
MAX_ATSOP_ROWS = 10
ATSOP_GAP=2 // seconds
ATSOP = ATSOP_GAP
SD = 1
CELL = 1
WIDTH = 50 // for grid in px
cnt =0 // for path_dots

function recordFeedback(cell, action, reaction){
  // console.log("record feedback", cell,action, reaction, "end")
  if(reaction == 'down'){
      if(ATSOP > MAX_ATSOP_ROWS*ATSOP_GAP){
        next_cell = cell
      }else{
        next_cell = cell +1
        if(ATSOP!= MAX_ATSOP_ROWS*ATSOP_GAP){
        drawDot('top', action)
      }
    }
  }else if(reaction == 'right'){
      SD +=1
      if(SD > MAX_SD_COLS){
        SD -= 1
        next_cell = cell +1
        drawDot('top', action)
      }else{
        next_cell = cell + MAX_ATSOP_ROWS
        drawDot('left', action)
      }
  }else{
    next_cell == 1000
    FEEDBACK.push({'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})

    $.ajax({
      url: "http://0.0.0.0:9090/feedback",
      contentType: 'application/json; charset=UTF-8',
      data: JSON.stringify({feedback: FEEDBACK}),
      type:"POST",
    });
    window.location.href = "http://0.0.0.0:9090/"
  }
  FEEDBACK.push({'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})

  CELL = next_cell

}


function activateCounter(){
  var counter = setInterval(function(){
    console.log(ATSOP)


    if(CELL > MAX_ATSOP_ROWS * MAX_SD_COLS){
      reaction = 'dead'
      recordFeedback(CELL-1, 'nothing','dead')
    }
      ATSOP +=ATSOP_GAP
      CELL += 1
      recordFeedback(CELL-1,'nothing', 'down')
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

  $("#dot").css(attr, "+="+WIDTH+"px");
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

createGrid(MAX_ATSOP_ROWS, MAX_SD_COLS, WIDTH)
putLabelsOnGrid(MAX_ATSOP_ROWS, MAX_SD_COLS,ATSOP_GAP, WIDTH)
putTitlesOnGrid('Session Depth', 'Time Spent')
counter = activateCounter()

controller('stop', 'video')
controller('start', 'down')
controller('stop', 'rec')
controller('start', 'right')
controller('stop','paywall')
controller('start','down')
