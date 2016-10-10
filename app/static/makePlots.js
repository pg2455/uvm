
function updatePlots(x_labels, y_labels){44444444444
  // draw Q
  $.ajax({
    dataType:'json',
    url:'/getQ',
    type:"GET",
    success:function(data){
      for(segment in data){
        count=0
        for(i in data[segment]){
          div = segment+'QDiv'+count
          drawHeatMap(div, data[segment][i], i, count == Object.keys(data).length-1,x_labels, y_labels)
          count+=1
        }
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
      // console.log(data);
      // return
      count =0
      sim_count = 2
      for(segment in data){
        div = segment+'VDiv'
        drawHeatMap(div, data[segment]['V'],'Value Matrix', true ,x_labels, y_labels)
        value1 = data[segment].value
        similarity1 = data[segment].similarity
        value = MathJax.Hub.getAllJax("value_user")[count];
        similarity = MathJax.Hub.getAllJax("similarity")[sim_count];
        QUEUE.Push(["Text", value, "$"+round(value1, 2) ]);
        QUEUE.Push(["Text",similarity, round(similarity1, 2) ])

        count++;
        sim_count+=2; // diff structure there
      }
      updateValue(parseFloat($("#N_in").attr('value')));
      // value1 = data.value
      // console.log(value1, data.V)
      // value = MathJax.Hub.getAllJax("value_user")[0];
      // QUEUE.Push(["Text", value, "$"+round(value1, 2) ])
      // updateValue(parseFloat($("#N_in").attr('value')))
    },
    cache:false
  });

  // draw policy
  $.ajax({
    dataType:'json',
    url:'/getPolicy',
    type:"GET",
    success:function(data){
      for(segment in data){
        if(data[segment]['SARSA'] == true){
          title = 'SARSA Optimal Policy'
        }else{
          title = 'Locally Optimal Policy'
        }
        div = segment+'OPolicyDiv'
        drawHeatMap(div, data[segment]['number'],title, true ,x_labels, y_labels, data[segment]['policy'])
      }
    },
    cache:false
  });

  // draw used policy
  $.ajax({
    dataType:'json',
    url:'/getUsedPolicy',
    type:"GET",
    success:function(data){
      for(segment in data){
        div = segment+'UPolicyDiv'
        drawHeatMap(div, data[segment]['number'],'Used Policy', true ,x_labels, y_labels, data[segment]['policy'])
      }
    },
    cache:false
  });

  // display pages and values
  $.ajax({
    dataType:'json',
    url:'/getPages',
    type:"GET",
    success:function(data){
      for(segment in data){
        pages = data[segment]['pages']
        div = segment+'pagesTable'
        $('#' +div+' > tbody').empty()

        for(i in pages){

          for(sd in pages[i]){
            parent  = $('<tr/>').appendTo('#' +div+' > tbody')
            parent.append('<td>'+ i + '</td>')
            parent.append('<td>' + sd + '</td>')

            for(a in ACTIONS){
              parent.append('<td>' + pages[i][sd][ACTIONS[a]] + '</td>')
            }

          }
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
      for(segment in data){
        if(data[segment]['OptV'].length != 0){
          div = segment+'OVDiv'
          drawHeatMap(div, data[segment]['OptV'],'Optimal Value Matrix', true ,x_labels, y_labels)
        }else{
          $("#"+segment+"ODiv").empty()
        }
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
    zmin:-1,
    zmax:1,
    x:x,
    y:y,
    //custom colorscale; this makes sure different maps are on same scale
    colorscale: [[0, 'rgb(227,26,28)'], [0.25, 'rgb(251,154,153)'], [0.45, 'rgb(51,160,44)'], [0.65,'rgb(178,223,138)' ], [0.85,'rgb(31,120,180)' ], [1,'rgb(166,206,227)' ]],

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
  if (value == 0){
    return 0.0
  }
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}

function updateValue(N){
  if(QUEUE.queue.length==0){
    money = MathJax.Hub.getAllJax("rhs")[0];
    values = MathJax.Hub.getAllJax("value_user")
    similarity = MathJax.Hub.getAllJax("similarity")
    sim_count = 2
    sum = 0
    for(i in values){
      v= parseFloat(values[i].originalText.slice(1))
      s = parseFloat(similarity[sim_count].originalText)
      // console.log(v,s, similarity[sim_count].originalText, values[i].originalText)
      sim_count +=2
      sum +=v*s
    }
    QUEUE.Push(["Text", money, "\\displaystyle{$"+ round(sum*N, 2) + "}" ])
  }else{
    setTimeout(function(){console.log(1);updateValue(N)}, 1500)
  }

}
