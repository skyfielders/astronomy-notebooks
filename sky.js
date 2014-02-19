activate_sky_display = function(d3) {
    var width = 560;
    var height = 560;

    var projection = d3.geo.azimuthalEqualArea()
        .scale(200)
        .translate([width / 2, height / 2])
        .clipAngle(90);

    var path = d3.geo.path()
        .projection(projection)
        .pointRadius(function(feature) {return 2 - feature['magnitude'] / 3;});

    var λ = d3.scale.linear()
        .domain([0, width])
        .range([-180, 180]);

    var φ = d3.scale.linear()
        .domain([0, height])
        .range([90, -90]);

    var svg = d3.select('#UNIQUE_ID').append('svg')
        .attr('width', width)
        .attr('height', height);

    var starpaths = svg.append('g');

    svg.on('mousemove', function() {
        var p = d3.mouse(this);
        projection.rotate([λ(p[0]), φ(p[1])]);
        svg.selectAll('path').attr('d', path);
    });

    starpaths.selectAll('path').data(star_data)
        .enter()
        .append('path')
        .attr('class', function(d) {return 'star-' + d.color})
        .attr('d', path);

    console.log('up and running!');
};

if (typeof define === 'function' && define.amd) {
    /* We are inside a live IPython Notebook and must use RequireJS */

    require.config({paths: {d3: 'http://d3js.org/d3.v3.min'}});
    require(['d3'], function(d3) {
        activate_sky_display(d3);
    });
} else {
    /* We are in the IPython Notebook Viewer and must shift for ourselves */

    var d3_script_tag = document.createElement('script');
    d3_script_tag.setAttribute('src', 'http://d3js.org/d3.v3.min');
    document.head.appendChild(d3_script_tag);

    window.addEventListener('DOMContentLoaded', function() {
        activate_sky_display(d3);
    }, false);
}
