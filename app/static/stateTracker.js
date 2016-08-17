atsop=0
interval = 1000 // ms
CURRENT_CELL=1
FEEDBACK= []
console.log(atsop)
window.setInterval(function() {

  action = chooseAction(ACTION_PROB)
  takeAction(action)

  if(screenBlocked == false){
    atsop += PARAMETERS['ATSOP_GAP']

    if (atsop <= 9){
      CURRENT_CELL+=1
    }else{
      CURRENT_CELL +=MAX_ATSOP_ROWS
    }
    if(CURRENT_CELL >9){
      reaction = 'dead'
      recordFeedback(CURRENT_CELL-1, 'nothing', 'dead')
      window.location.href ="http://0.0.0.0:9090/"
    }
    console.log(atsop)
  }
}, 3*1000)


function recordFeedback(cell, action, reaction){
  // console.log("record feedback", cell,action, reaction, "end")
  if(reaction == 'down'){
    next_cell = cell +1
  }else if(reaction == 'right'){
    next_cell = cell + MAX_ATSOP_ROWS
  }else{
    next_cell == 1000
    // window.location.href = "http://0.0.0.0:9090/"
  }
  FEEDBACK.push({'prev_state':cell, 'action':action, 'reaction':reaction, 'next_state':next_cell})

  CURRENT_CELL = next_cell

}
