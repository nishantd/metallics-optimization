$(document).ready(() => {

    $.ajax({
        headers: {"Accept": "application/json"},
        type: 'GET',
        url: 'http://127.0.0.1:8001/plots/prices',
        crossDomain: true,
        success: (res) => {
            console.log(res);
            const prices = res;

            update_plot(prices);
        }
    });

    function update_plot(prices) {

        let x = Object.keys(prices);
        let y = Object.values(prices);

        y = y.map(val => val * 1000);

        let data = [{
            type: 'bar',
            x: y,
            y: x,
            orientation: 'h',
            text: y.map((x) => x.toFixed(2)).map(x => '$' + String(x)),
            textposition: 'auto',
            hoverinfo: 'none',
            marker: {color: "rgb(50,171, 96)"},
        }];

        let layout = {

            xaxis: {
                title: {
                    text: 'Average scrap price ($ per ton)',
                    font: {
                        size: 14,
                        color: '#7f7f7f'
                    }
                },
                autotick: true
            }
        };


        Plotly.newPlot('div-plot', data, layout);
    }
});