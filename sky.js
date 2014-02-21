activate_sky_display = function(d3) {

    for (var con in boundary_data) {
        var boundary = boundary_data[con];
        var radec_array = boundary.coordinates[0];
        for (var i = 0; i < radec_array.length; i++) {
            var radec = radec_array[i];
            radec[0] = -radec[0] / 240.0;  /* seconds of RA to degrees */
            radec[1] = radec[1] / 60.0;    /* arcminutes to degrees */
        }
        if (d3.geo.area(boundary) > 6.0)
            boundary.coordinates[0].reverse();
    }

    var ser1 = boundary_data.SER1;
    var ser2 = boundary_data.SER2;
    delete boundary_data.SER1;
    delete boundary_data.SER2;
    ser1.coordinates.push(ser2.coordinates[0]);
    boundary_data.SER = ser1;

    var width = 560;
    var height = 560;

    var constellation_at = function(ra, dec) {
        n = decision_data.length;
        for (i = 0; i < n; i++) {
            row = decision_data[i];
            if ((dec >= row[2]) && (row[0] <= ra) && (ra < row[1]))
                return row[3];
        }
        return row[3];
    };

    var projection = d3.geo.azimuthalEqualArea()
        .scale(200)
        .translate([width / 2, height / 2])
        .clipAngle(90);

    var path = d3.geo.path()
        .projection(projection)
        .pointRadius(function(feature) {return 2 - feature['magnitude'] / 3;});

    var λ = d3.scale.linear()
        .domain([0, width])
        .range([0, 370]);

    var φ = d3.scale.linear()
        .domain([0, height])
        .range([90, -90]);

    var constellation_p = d3.select('#UNIQUE_ID').append('p');

    var svg = d3.select('#UNIQUE_ID').append('svg')
        .attr('width', width)
        .attr('height', height);

    var current_constellation = 'ORI';

    var constellation = svg.append('g').attr('class', 'constellation');
    var starpaths = svg.append('g');

    constellation.selectAll('path')
        .data([boundary_data[current_constellation]])
        .enter()
        .append('path')
        .attr('d', path);

    starpaths.selectAll('path')
        .data(star_data)
        .enter()
        .append('path')
        .attr('class', function(d) {return 'star-' + d.color})
        .attr('d', path);

    svg.on('mousemove', function() {
        var p = d3.mouse(this);
        var ra = λ(p[0]) % 360.0;
        var dec = φ(p[1]);
        var con = constellation_at(ra, -dec);
        projection.rotate([ra, dec]);
        if (con != current_constellation) {
            current_constellation = con;
            constellation_p.text(con);
            constellation.selectAll('path')
                .data([boundary_data[current_constellation]]);
        }
        svg.selectAll('path').attr('d', path);
    });

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
    d3_script_tag.src = 'http://d3js.org/d3.v3.min.js';
    d3_script_tag.async = true;
    d3_script_tag.onreadystatechange = d3_script_tag.onload = function() {
        var callback = activate_sky_display;
        var state = d3_script_tag.readyState;
        if (!callback.done && (!state || /loaded|complete/.test(state))) {
            callback.done = true;
            callback(d3);
        }
    };
    document.getElementsByTagName('head')[0].appendChild(d3_script_tag);
}
