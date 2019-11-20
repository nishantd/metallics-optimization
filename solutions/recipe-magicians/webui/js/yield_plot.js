$(document).ready(() => {

    $.ajax({
        headers: {"Accept": "application/json"},
        type: 'GET',
        url: 'http://127.0.0.1:8001/plots/yield',
        crossDomain: true,
        success: (res) => {
            console.log(res);
            const yield_data = res;

            $('#steel-grade-select').change(() => {
                update_plot(yield_data);
            });

            update_plot(yield_data);
        }
    });

    function update_plot(yield_data) {
        let grade = $('#steel-grade-select').val();
        let grade_yield = yield_data[grade];

        let data = [{
            type: 'bar',
            x: grade_yield['y'],
            y: grade_yield['x'],
            orientation: 'h',
            text: grade_yield['y'].map((x) => x.toFixed(4)).map(String),
            textposition: 'auto',
            hoverinfo: 'none'
        }];

        let layout = {

            xaxis: {
                title: {
                    text: 'Expected yield (%)',
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


    //update_plot();
});