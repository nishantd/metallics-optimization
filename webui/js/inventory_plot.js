$(document).ready(() => {

    $.ajax({
        headers: {"Accept": "application/json"},
        type: 'GET',
        url: 'http://127.0.0.1:8001/plots/inventory',
        crossDomain: true,
        success: (res) => {
            console.log(res);
            const inventory_data = res;

            update_plot(inventory_data);
        }
    });

    function update_plot(inventory_data) {

        let data = [{
            type: 'pie',
            values: inventory_data['values'],
            labels: inventory_data['labels'],
            textposition: "outside",
            textinfo: "label+percent+value",
            hole: 0.3
        }];

        let layout = {
            height: 500,
        };


        Plotly.newPlot('div-plot', data, layout);
    }


    //update_plot();
});