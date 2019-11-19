$(document).ready(() => {

    $.ajax({
        headers: {"Accept": "application/json"},
        type: 'GET',
        url: 'http://127.0.0.1:8001/plots/copper',
        crossDomain: true,
        success: (res) => {
            console.log(res);
            const copper_data = res;

            $('#steel-grade-select').change(() => {
                update_plot(copper_data);
            });

            update_plot(copper_data);
        }
    });

    function update_plot(yield_data) {
        let grade = $('#steel-grade-select').val();
        let grade_copper = yield_data[grade];

        let x = grade_copper['x'];
        let y = grade_copper['y'].map(val => val * 1000 * 1000);

        let data = [{
            type: 'bar',
            x: y,
            y: x,
            orientation: 'h',
            text: y.map(x => x.toFixed(4)).map(String),
            textposition: 'auto',
            hoverinfo: 'none',
            marker: {color: "#ff7f0e"},
        }];

        let layout = {

            xaxis: {
                title: {
                    text: 'Expected copper amount (g per 1 ton)',
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