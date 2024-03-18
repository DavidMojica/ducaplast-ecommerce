let option;
let chart1;
// let chart2;

const getOptionChart1 = () =>{
    return {
        title: {
            text: 'Clientes más frecuentes',
            subtext: "Top 8",
            x: 'center',
        },
        legend: {
            top: 'bottom'
        },
        toolbox: {
            show: true,
            feature: {
                mark: { show: true },
            }
        },
        series: [
          {
            name: 'Clientes más frecuentes',
                type: 'pie',
                radius: [40, 160],
                center: ['50%', '50%'],
                roseType: 'area',
                itemStyle: {
                borderRadius: 8
            },
            data: [
              { value: 40, name: 'DUMMI SAS' },
              { value: 38, name: 'Panaderia la 80' },
              { value: 32, name: 'Viajes SAS' },
              { value: 30, name: 'Trans Gavirias SAS' },
              { value: 28, name: 'Bolivariano' },
              { value: 26, name: 'Trans Medellin' },
              { value: 22, name: 'Emtelco' },
              { value: 18, name: 'UNE' }
            ]
          }
        ]
      };
}

const initCharts =()=>{
    chart1 = echarts.init(document.getElementById("chart1"));
    option = getOptionChart1(); 
    chart1.setOption(option); 

    // chart2 = echarts.init(document.getElementById("chart2"));
    // option = getOptionChart2();
    // chart2.setOption(option); 
}
document.addEventListener('DOMContentLoaded', function () {
    initCharts();
});

window.addEventListener('resize', function () {
    chart1.resize();
    // chart2.resize();
})