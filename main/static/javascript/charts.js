let option;
let chart1;
let chart2;


//Example charts
const getOptionChart1 = async () =>{
    try{
      const response = await fetch("http://127.0.0.1:8000/get_chart_1/")
      return await response.json();
    } catch (ex){
      console.log(ex);
    }
}

const getOptionChart2 = () => {
    return {
      title: {
        text: 'Días más concurridos',
        subtext: "Ventas promedio en los días de la semana",
        x: 'center',
      },
        xAxis: {
          type: 'category',
          data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: [
              120,
              {
                value: 200,
                itemStyle: {
                  color: '#a90000'
                }
              },
              150,
              80,
              70,
              110,
              130
            ],
            type: 'bar'
          }
        ]
    };
}

const initCharts = async ()=>{
    chart1 = echarts.init(document.getElementById("chart1"));
    chart1.setOption(await getOptionChart1()); 

    chart2 = echarts.init(document.getElementById("chart2"));
    option = getOptionChart2();
    chart2.setOption(option); 
}

document.addEventListener('DOMContentLoaded', function () {
    initCharts();
});

window.addEventListener('resize', function () {
    chart1.resize();
    chart2.resize();
})