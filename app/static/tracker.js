
// track clicks on link
function trackClicks(){
  $('a').click( function(s) {
    controller('stop','nothing')
    URL = s.currentTarget.href
    controller('start','right') // reaction is right
  });

  $('#restart').click(function(){
    reaction = 'dead'
    controller('stop', 'nothing')
    controller('start',reaction) // window will reset to start by itself
  })

}


function stumbleUpon(){
  list = $('a')
  data = []
  $.each(list, function(e){
    data.push(list[e].href)
  })
  num = Math.floor(Math.random() * data.length)
  return data[num]
}
