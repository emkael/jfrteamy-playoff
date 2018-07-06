var playoff = {

    settings: {
        'winner_h_offset': 5,
        'loser_h_offset': 20,
        'finish_winner_h_offset': 5,
        'finish_loser_h_offset': 20,
        'winner_v_offset': -10,
        'loser_v_offset': 10,
        'finish_winner_v_offset': -4,
        'finish_loser_v_offset': 4,
        'loser_colour': '#ff0000',
        'winner_colour': '#00ff00',
        'place_winner_h_offset': 10,
        'place_loser_h_offset': 15,
        'place_winner_v_offset': 8,
        'place_loser_v_offset': 14,
        'place_loser_colour': '#dddd00',
        'place_winner_colour': '#00dddd',
        'finish_loser_colour': '#ff0000',
        'finish_winner_colour': '#00ff00'
    },

    drawLine: function(ctx, line) {
        ctx.beginPath();
        ctx.moveTo(line[0], line[1]);
        ctx.lineTo(line[2], line[3]);
        ctx.stroke();
    },

    loadSettings: function(canvas, defaults) {
        for (var setting in defaults) {
            var attr = 'data-' + setting.replace(/_/g, '-');
            var attr_value = canvas.getAttribute(attr);
            if (attr_value) {
                defaults[setting] = attr_value;
            }
        }
        return defaults;
    },

    run: function() {
        var boxes = document.getElementsByClassName('playoff_matchbox');
        var lines = {
            'winner': {},
            'loser': {},
            'place-winner': {},
            'place-loser': {},
            'finish-winner': {},
            'finish-loser': {}
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
        this.settings = this.loadSettings(canvas, this.settings);
        var lineMethods = {
            'place-winner': 'to',
            'place-loser': 'to',
            'finish-winner': 'midpoint',
            'finish-loser': 'midpoint',
            'winner': 'midpoint',
            'loser': 'midpoint'
        };
        var lineCalculator = {
            correctLines: function(hLines, vLine, comparator) {
                for (var l1 in hLines) {
                    for (var l2 in hLines) {
                        hLines[l1][2] = comparator(hLines[l1][2], hLines[l2][2]);
                        hLines[l2][2] = hLines[l1][2];
                    }
                }
                for (var l1 in hLines) {
                    vLine[0] = vLine[2] = comparator(hLines[l1][2], vLine[2]);
                    vLine[1] = Math.min(vLine[1], hLines[l1][3]);
                    vLine[3] = Math.max(vLine[3], hLines[l1][3]);
                }
            },
            template: function() {
                return {
                    hFrom: [],
                    vFrom: [0, canvas.height, 0, 0],
                    hTo: [],
                    vTo: [canvas.width, canvas.height, canvas.width, 0],
                    midpoints: []
                }
            },
            from: function(from, to, hOffset, vOffset) {
                var lines = this.template();
                for (var f = 0; f < from.length; f++) {
                    var box = boxes_idx[from[f]];
                    var line = [
                        Math.floor(parseInt(box.offsetLeft) + parseInt(box.clientWidth)),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        Math.floor(parseInt(box.offsetLeft) + parseInt(box.clientWidth) + hOffset),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hFrom.push(line);
                }
                this.correctLines(lines.hFrom, lines.vFrom, Math.max);
                for (var t = 0; t < to.length; t++) {
                    var box = boxes_idx[to[t]];
                    var line = [
                        Math.floor(parseInt(box.offsetLeft)),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        lines.vFrom[0],
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hTo.push(line);
                }
                this.correctLines(lines.hTo, lines.vTo, Math.min);
                lines.midpoints = [
                    [lines.vFrom[0], lines.vFrom[1]],
                    [lines.vTo[0], lines.vTo[1]]
                ];
                return lines;
            },
            to: function(from, to, hOffset, vOffset) {
                var lines = this.template();
                for (var t = 0; t < to.length; t++) {
                    var box = boxes_idx[to[t]];
                    var line = [
                        parseInt(box.offsetLeft),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        Math.floor(parseInt(box.offsetLeft) - hOffset),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hTo.push(line);
                }
                this.correctLines(lines.hTo, lines.vTo, Math.min);
                for (var f = 0; f < from.length; f++) {
                    var box = boxes_idx[from[f]];
                    var line = [
                        Math.floor(parseInt(box.offsetLeft) + parseInt(box.clientWidth)),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        lines.vTo[0],
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hFrom.push(line);
                }
                this.correctLines(lines.hFrom, lines.vFrom, Math.max);
                lines.midpoints = [
                    [lines.vFrom[0], lines.vFrom[1]],
                    [lines.vTo[0], lines.vTo[1]]
                ];
                return lines;
            },
            midpoint: function(from, to, hOffset, vOffset) {
                var lines = this.template();
                for (var f = 0; f < from.length; f++) {
                    var box = boxes_idx[from[f]];
                    var line = [
                        Math.floor(parseInt(box.offsetLeft) + parseInt(box.clientWidth)),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        Math.floor(parseInt(box.offsetLeft) + parseInt(box.clientWidth) + hOffset),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hFrom.push(line);
                }
                this.correctLines(lines.hFrom, lines.vFrom, Math.max);
                for (var t = 0; t < to.length; t++) {
                    var box = boxes_idx[to[t]];
                    var line = [
                        parseInt(box.offsetLeft),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset),
                        Math.floor(parseInt(box.offsetLeft) - hOffset),
                        Math.floor(parseInt(box.offsetTop) + 0.5 * parseInt(box.clientHeight) + vOffset)
                    ];
                    lines.hTo.push(line);
                }
                this.correctLines(lines.hTo, lines.vTo, Math.min);
                lines.midpoints = [
                    [
                        (lines.vFrom[0] + lines.vFrom[2]) / 2,
                        (lines.vFrom[1] + lines.vFrom[3]) / 2
                    ],
                    [
                        hOffset / 2 + (lines.vFrom[0] + lines.vFrom[2] + lines.vTo[0] + lines.vTo[2]) / 4,
                        (lines.vFrom[1] + lines.vFrom[3]) / 2
                    ],
                    [
                        hOffset / 2 + (lines.vFrom[0] + lines.vFrom[2] + lines.vTo[0] + lines.vTo[2]) / 4,
                        (lines.vTo[1] + lines.vTo[3]) / 2
                    ],
                    [
                        (lines.vTo[0] + lines.vTo[2]) / 2,
                        (lines.vTo[1] + lines.vTo[3]) / 2
                    ]
                ]
                return lines;
            }
        };
        var ctx = canvas.getContext('2d');
        for (var type in lines) {
            styleType = type.replace('-', '_');
            ctx.strokeStyle = this.settings[styleType + '_colour'];
            for (var from in lines[type]) {
                var to = lines[type][from];
                from = from.split(' ');
                var linesToDraw = lineCalculator[lineMethods[type]](
                    from, to,
                    this.settings[styleType + '_h_offset'], this.settings[styleType + '_v_offset']);
                for (var l in linesToDraw.hFrom) {
                    this.drawLine(ctx, linesToDraw.hFrom[l]);
                }
                this.drawLine(ctx, linesToDraw.vFrom);
                for (var l in linesToDraw.hTo) {
                    this.drawLine(ctx, linesToDraw.hTo[l]);
                }
                this.drawLine(ctx, linesToDraw.vTo);
                for (var m = 0; m < linesToDraw.midpoints.length-1; m++) {
                    this.drawLine(ctx, [
                        linesToDraw.midpoints[m][0], linesToDraw.midpoints[m][1],
                        linesToDraw.midpoints[m+1][0], linesToDraw.midpoints[m+1][1]
                    ]);
                }
            }
        }
    }

}

playoff.run();
