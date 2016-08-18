// var connection = new WebSocket('ws://0.0.0.0:9090/statusUpdate')
//
// connection.onopen = function(){
//   connection.send('Ping')
// };
//
// connection.onerror = function(error){
//   console.log('WebSocket Error' + error)
// };
//
// connection.onmessage = function(e){
//   console.log('Server:', e)
// };


function updatePlots(){
  // draw Q
  $.ajax({
    dataType:'json',
    url:'/getQ',
    type:"GET",
    success:function(data){
      count =0
      console.log(data)
      for(i in data){
        div = 'QDiv'+count
        drawHeatMap(div, data[i], i, count == Object.keys(data).length-1)
        count+=1
      }
    }
  });


  // draw V

  // draw policy

  // display pages and values

}




function drawHeatMap(div, Q, action, legend){
  var data = [{
    // data
    // z: [[1,2,3],[3,2,1]],

    z: Q,
    x:[1,2,3],
    y:['20-30','10-20','0-10'],
    //custom colorscale; this makes sure different maps are on same scale
    colorscale: [[0, 'rgb(166,206,227)'], [0.25, 'rgb(31,120,180)'], [0.45, 'rgb(178,223,138)'], [0.65, 'rgb(51,160,44)'], [0.85, 'rgb(251,154,153)'], [1, 'rgb(227,26,28)']],

    //grey colorscale
    // colorscale: 'Greys',

    // heatmap
    type: 'heatmap'
  }];

  // axes
  var layout = {
    title: action,
    xaxis: {
      // type:"category",
      title:"Session Depth",
      // tickvals:[1,2,3],
      showticklabels:true,
      // ticks:'',
      showgrid:true,
    },
    yaxis:{
      // type:"category",
      showgrid:true,
      // tickvals:['10-20','0-10'],
      showticklabels:true,
      title:"Time Spent in the session",
      ticks: ''
    },
    showscale:legend,
    showlegend:legend,
    opacity:0.8,
    annotations: [],
    reversescale:true
  };

  //annotations
  tmp = data[0]
  for(i=0; i<tmp.y.length; i++){
    for(j=0; j<tmp.x.length; j++){
      value = tmp.z[i][j]

      annot= {
        xref:'x1',
        yref:'y1',
        x:tmp.x[j],
        y:tmp.y[i],
        text:round(value,2),
        showarrow:false,
        font:{
          color:'black'
        }
      }
      layout.annotations.push(annot)
    }
  }
  // make it
  Plotly.newPlot(div, data, layout);
}


function round(value, decimals) {
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}
