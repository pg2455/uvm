
function updatePlots(x_labels, y_labels){
  // draw Q
  $.ajax({
    dataType:'json',
    url:'/getQ',
    type:"GET",
    success:function(data){
      count =0

      for(i in data){
        div = 'QDiv'+count
        drawHeatMap(div, data[i], i, count == Object.keys(data).length-1,x_labels, y_labels)
        count+=1
      }
    },
    cache:false
  });


  // draw V

  $.ajax({
    dataType:'json',
    url:'/getV',
    type:"GET",
    success:function(data){

      value1 = data.value
      console.log(value1, data.V)
      value = MathJax.Hub.getAllJax("value_user")[0];
      QUEUE.Push(["Text", value, "$"+round(value1, 2) ])
      updateValue(parseFloat($("#N_in").attr('value')))

      div = 'VDiv'
      drawHeatMap(div, data['V'],'Value Matrix', true ,x_labels, y_labels)
    },
    cache:false
  });

  // draw policy
  $.ajax({
    dataType:'json',
    url:'/getPolicy',
    type:"GET",
    success:function(data){
      if(data['SARSA'] == true){
        title = 'SARSA Optimal Policy'
      }else{
        title = 'Locally Optimal Policy'
      }
      div = 'OPolicyDiv'
      drawHeatMap(div, data['number'],title, true ,x_labels, y_labels, data['policy'])
    },
    cache:false
  });

  // draw used policy
  $.ajax({
    dataType:'json',
    url:'/getUsedPolicy',
    type:"GET",
    success:function(data){
      div = 'UPolicyDiv'
      drawHeatMap(div, data['number'],'Used Policy', true ,x_labels, y_labels, data['policy'])
    },
    cache:false
  });

  // display pages and values
  $.ajax({
    dataType:'json',
    url:'/getPages',
    type:"GET",
    success:function(data){
        pages = data['pages']
        $('#pagesTable > tbody').empty()
        for(i in pages){
          parent  = $('<tr/>').appendTo('#pagesTable > tbody')

          parent.append('<td>'+ i + '</td>')
          for(a in ACTIONS){

            parent.append('<td>' + pages[i][ACTIONS[a]] + '</td>')
          }
        }
    },
    cache:false
  });

  //draw optimal V
  $.ajax({
    dataType:'json',
    url:'/getOptV',
    type:"GET",
    success:function(data){

      if(data['OptV'].length != 0){
        div = 'OVDiv'
        drawHeatMap(div, data['OptV'],'Optimal Value Matrix', true ,x_labels, y_labels)
      }else{
        $("#ODiv").empty()
      }
    },
    cache:false
  });

}


function drawHeatMap(div, Q, action, legend,x,y,z_annot = 0){
  var data = [{
    // data
    // z: [[1,2,3],[3,2,1]],

    z: Q,
    x:x,
    y:y,
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
      tickvals:x,
      showticklabels:true,
      ticks:'',
      showgrid:true,
    },
    yaxis:{
      type:"category",
      showgrid:true,
      tickvals:y,
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

  if(z_annot==0){
    //annotations
    tmp = data[0]
  }else{
    tmp = {
      x:data[0].x,
      y:data[0].y,
      z:z_annot
    }
  }

  for(i=0; i<tmp.y.length; i++){
    for(j=0; j<tmp.x.length; j++){

      if(z_annot == 0){
        value = round(tmp.z[i][j],2)
      }else{
        value = tmp.z[i][j]
      }

      annot= {
        xref:'x1',
        yref:'y1',
        x:tmp.x[j],
        y:tmp.y[i],
        text:value,
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
