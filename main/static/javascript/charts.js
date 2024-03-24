let option;
let chart1, chart2, chart3, chart4;

const domain = "http://127.0.0.1:8000/"

//Example charts
const getOptionChart1 = async () =>{
    try{
      const response = await fetch(domain+"get_chart_1/");
      return await response.json();
    } catch (ex){
      console.log(ex);
    }
}

const getOptionChart2 = async () => {
  try{
    const response = await fetch(domain+"get_chart_2/");
    return await response.json();
  } catch (ex){
    console.log(ex);
  }
}

const getOptionChart3 = async () => {
  try{
    const response = await fetch(domain+"get_chart_3/");
    return await response.json();
  } catch (ex){
    console.log(ex);
  }
}

const initCharts = async ()=>{
    chart1 = echarts.init(document.getElementById("chart1"));
    chart1.setOption(await getOptionChart1()); 

    chart2 = echarts.init(document.getElementById("chart2"));
    chart2.setOption(await getOptionChart2()); 

    chart3 = echarts.init(document.getElementById("chart3"));
    chart3.setOption(await getOptionChart3()); 
  
}

document.addEventListener('DOMContentLoaded', function () {
    initCharts();
});

window.addEventListener('resize', function () {
    chart1.resize();
    chart2.resize();
    chart3.resize();
})