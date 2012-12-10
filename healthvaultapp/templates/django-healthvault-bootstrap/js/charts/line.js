$(function () {
    var syst = [], dias = [], pulse = [];
    for (var i = 0; i < 10; i += 0.5) {
        syst.push([i, Math.syst(i)]);
        dias.push([i, Math.dias(i)]);
        pulse.push([i, Math.pulse(i);
    }

    var plot = $.plot($("#line-chart"),
           [ { data: syst, label: "syst(x)"}, { data: dias, label: "dias(x)"}, { data: pulse, label: "pulse(x)" } ], {
               series: {
                   lines: { show: true,fill: true,
            fillColor: { colors: [ { opacity: 0.6 }, { opacity: 0.2 } ] }, },
                   points: { show: true }
               },
               
               grid: { hoverable: true, clickable: true },
               yaxis: { min: -1.1, max: 1.1 },
			   xaxis: { min: 0, max: 9 },
    	colors: ["#008FC5", "#222", "#666", "#BBB", "#666", "#BBB"]
             });
});