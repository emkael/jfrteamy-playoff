var playoff = {

    settings: {
        'winner_h_offset': 10,
        'loser_h_offset': 20,
        'winner_v_offset': -4,
        'loser_v_offset': 4,
        'loser_colour': '#ff0000',
        'winner_colour': '#00ff00'
    },

    drawLine: function(ctx, line) {
        ctx.beginPath();
        ctx.moveTo(line[0], line[1]);
        ctx.lineTo(line[2], line[3]);
        ctx.stroke();
    },

    run: function() {
        var boxes = document.getElementsByClassName('playoff_matchbox');
        var lines = {
            'winner': {},
            'loser': {}
        };
        var boxes_idx = {};
        for (var b = 0; b < boxes.length; b++) {
            var id = boxes[b].getAttribute('data-id');
            boxes_idx[id] = boxes[b];
            for (var attr in lines) {
                var value = boxes[b].getAttribute('data-' + attr);
                if (value) {
                    if (!lines[attr][value]) {
                        lines[attr][value] = [];
                    }
                    lines[attr][value].push(id);
                }
            }
        }
        var canvas = document.getElementById('playoff_canvas');
        var ctx = canvas.getContext('2d');
        for (var type in lines) {
            ctx.strokeStyle = this.settings[type + '_colour'];
            for (var from in lines[type]) {
                var to = lines[type][from];
                from = from.split(' ');
                var horizontal_from = [];
                var vertical_from = [0, canvas.height, 0, 0];
                for (var f = 0; f < from.length; f++) {
                    var box = boxes_idx[from[f]];
                    var line = [
                        parseInt(box.style.left) + parseInt(box.clientWidth),
                        parseInt(box.style.top) + 0.5 * parseInt(box.clientHeight) + this.settings[type + '_v_offset'],
                        parseInt(box.style.left) + parseInt(box.clientWidth) + this.settings[type + '_h_offset'],
                        parseInt(box.style.top) + 0.5 * parseInt(box.clientHeight) + this.settings[type + '_v_offset']
                    ];
                    horizontal_from.push(line);
                    for (var l in horizontal_from) {
                        if (horizontal_from[l][2] < line[2]) {
                            horizontal_from[l][2] = line[2];
                        }
                        if (vertical_from[0] < horizontal_from[l][2]) {
                            vertical_from[0] = horizontal_from[l][2];
                            vertical_from[2] = horizontal_from[l][2];
                        }
                        if (vertical_from[1] > horizontal_from[l][3]) {
                            vertical_from[1] = horizontal_from[l][3];
                        }
                        if (vertical_from[3] < horizontal_from[l][3]) {
                            vertical_from[3] = horizontal_from[l][3];
                        }
                    }
                }
                var horizontal_to = [];
                var vertical_to = [canvas.width, canvas.height, canvas.width, 0];
                for (var t = 0; t < to.length; t++) {
                    var box = boxes_idx[to[t]];
                    var line = [
                        parseInt(box.style.left),
                        parseInt(box.style.top) + 0.5 * parseInt(box.clientHeight) + this.settings[type + '_v_offset'],
                        parseInt(box.style.left) - this.settings[type + '_h_offset'],
                        parseInt(box.style.top) + 0.5 * parseInt(box.clientHeight) + this.settings[type + '_v_offset']
                    ];
                    horizontal_to.push(line);
                    for (var l in horizontal_to) {
                        if (horizontal_to[l][2] > line[2]) {
                            horizontal_to[l][2] = line[2];
                        }
                        if (vertical_to[0] > horizontal_to[l][2]) {
                            vertical_to[0] = horizontal_to[l][2];
                            vertical_to[2] = horizontal_to[l][2];
                        }
                        if (vertical_to[1] > horizontal_to[l][3]) {
                            vertical_to[1] = horizontal_to[l][3];
                        }
                        if (vertical_to[3] < horizontal_to[l][3]) {
                            vertical_to[3] = horizontal_to[l][3];
                        }
                    }
                }
                var midpoints = [
                    [
                        (vertical_from[0] + vertical_from[2]) / 2,
                        (vertical_from[1] + vertical_from[3]) / 2
                    ],
                    [
                        this.settings[type + '_v_offset'] + (vertical_from[0] + vertical_from[2] + vertical_to[0] + vertical_to[2]) / 4,
                        (vertical_from[1] + vertical_from[3]) / 2
                    ],
                    [
                        this.settings[type + '_v_offset'] + (vertical_from[0] + vertical_from[2] + vertical_to[0] + vertical_to[2]) / 4,
                        (vertical_to[1] + vertical_to[3]) / 2
                    ],
                    [
                        (vertical_to[0] + vertical_to[2]) / 2,
                        (vertical_to[1] + vertical_to[3]) / 2
                    ]
                ]
                for (var l in horizontal_from) {
                    this.drawLine(ctx, horizontal_from[l]);
                }
                this.drawLine(ctx, vertical_from);
                for (var l in horizontal_to) {
                    this.drawLine(ctx, horizontal_to[l]);
                }
                this.drawLine(ctx, vertical_to);
                for (var m = 0; m < midpoints.length-1; m++) {
                    this.drawLine(ctx, [
                        midpoints[m][0], midpoints[m][1], midpoints[m+1][0], midpoints[m+1][1]
                    ]);
                }
            }
        }
    }

}

playoff.run();
