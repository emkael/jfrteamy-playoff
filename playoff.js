var playoff = {

    settings: {
        'winner_h_offset': 5,
        'loser_h_offset': 20,
        'place_winner_h_offset': 10,
        'place_loser_h_offset': 15,
        'finish_winner_h_offset': 5,
        'finish_loser_h_offset': 20,
        'winner_v_offset': -10,
        'loser_v_offset': 10,
        'place_winner_v_offset': 2,
        'place_loser_v_offset': 9,
        'finish_winner_v_offset': -4,
        'finish_loser_v_offset': 4,
        'loser_colour': '#ff0000',
        'winner_colour': '#00ff00',
        'place_loser_colour': '#dddd00',
        'place_winner_colour': '#00dddd',
        'finish_loser_colour': '#ff0000',
        'finish_winner_colour': '#00ff00',
        'fade_boxes': 0
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
                if (attr.substr(attr.length-6) == 'offset') {
                    attr_value = parseInt(attr_value);
                }
                defaults[setting] = attr_value;
            }
        }
        return defaults;
    },

    initEvents: function() {
        this.settings = this.loadSettings(document.getElementById('playoff_canvas'), this.settings);
        var fadeInterval = this.settings['fade_boxes'];
        if (fadeInterval > 0) {
            var highlightTrigger;
            var boxes = document.getElementsByClassName('playoff_matchbox');
            var that = this;
            for (var b = 0; b < boxes.length; b++) {
                var box = boxes[b];
                var highlightHandler = this.highlightBox;
                box.addEventListener('mouseenter', function(evt) {
                    highlightTrigger = setTimeout(function() {
                        var boxId = evt.target.getAttribute('data-id');
                        that.highlightBox(boxId);
                        that.run(boxId);
                    }, fadeInterval);
                });
                box.addEventListener('mouseleave', function(evt) {
                    clearTimeout(highlightTrigger);
                    that.highlightBox();
                    that.run();
                });
            }
        }
    },

    highlightBox: function(box) {
        var boxes = document.getElementsByClassName('playoff_matchbox');
        var highlightBoxes = [];
        var attrArr = ['data-winner', 'data-loser', 'data-place-winner', 'data-place-loser', 'data-finish-winner', 'data-finish-loser'];
        for (var b = 0; b < boxes.length; b++) {
            var boxId = boxes[b].getAttribute('data-id');
            if (box && (boxId == box)) {
                highlightBoxes.push(boxId);
                for (const attr of attrArr) {
                    var attrVal = boxes[b].getAttribute(attr);
                    if (attrVal) {
                        highlightBoxes = highlightBoxes.concat(attrVal.split(' '));
                    }
                }
            }
            boxes[b].classList.remove('faded');
        }
        if (box) {
            for (var b = 0; b < boxes.length; b++) {
                var fade = true;
                var boxId = boxes[b].getAttribute('data-id');
                if (highlightBoxes.includes(boxId)) {
                    fade = false;
                } else {
                    for (const attr of attrArr) {
                        var boxId = boxes[b].getAttribute(attr);
                        if (boxId) {
                            boxIds = boxId.split(' ');
                            if (boxIds.includes(box)) {
                                fade = false;
                            }
                        }
                    }
                }
                if (fade) {
                    boxes[b].classList.add('faded');
                }
            }
        }
    },

    run: function(highlightedBox) {
        var boxes = document.getElementsByClassName('playoff_matchbox');
        var canvas = document.getElementById('playoff_canvas');
        var lines = {
            'winner': {},
            'loser': {},
            'place-winner': {},
            'place-loser': {},
            'finish-winner': {},
            'finish-loser': {},
            'winner-fade': {},
            'loser-fade': {},
            'place-winner-fade': {},
            'place-loser-fade': {},
            'finish-winner-fade': {},
            'finish-loser-fade': {}
        };
        var boxes_idx = {};
        for (var b = 0; b < boxes.length; b++) {
            var id = boxes[b].getAttribute('data-id');
            boxes_idx[id] = boxes[b];
            for (var attr in lines) {
                var value = boxes[b].getAttribute('data-' + attr);
                if (value) {
                    if (highlightedBox && (highlightedBox != id && !value.split(' ').includes(highlightedBox))) {
                        attr = attr + '-fade';
                    }
                    if (!lines[attr][value]) {
                        lines[attr][value] = [];
                    }
                    lines[attr][value].push(id);
                }
            }
        }
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
                };
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
                ];
                for (var h in lines.hTo) {
                    lines.hTo[h][2] = Math.max(
                        lines.hTo[h][2],
                        lines.midpoints[2][0]
                    );
                }
                for (var h in lines.hFrom) {
                    lines.hFrom[h][2] = Math.min(
                        lines.hFrom[h][2],
                        lines.midpoints[0][0]
                    );
                }
                return lines;
            }
        };
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        for (var type in lines) {
            ctx.globalAlpha = 1.0;
            realType = type;
            if (type.endsWith('-fade')) {
                realType = type.replace('-fade', '');
                ctx.globalAlpha = 0.3;
            }
            styleType = realType.replaceAll('-', '_');
            ctx.strokeStyle = this.settings[styleType + '_colour'];
            for (var from in lines[type]) {
                var to = lines[type][from];
                from = from.split(' ');
                var linesToDraw = lineCalculator[lineMethods[realType]](
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
                    if (linesToDraw.midpoints[m][0] <= linesToDraw.midpoints[m+1][0]) {
                        this.drawLine(ctx, [
                            linesToDraw.midpoints[m][0], linesToDraw.midpoints[m][1],
                            linesToDraw.midpoints[m+1][0], linesToDraw.midpoints[m+1][1]
                        ]);
                    }
                }
            }
        }
    }

};

playoff.initEvents();
playoff.run();
