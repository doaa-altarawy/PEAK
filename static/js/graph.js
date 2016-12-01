/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/*  Code snippit
// Get the data
data.forEach(function(d) {
    d.date = parseDate(d.date);
    d.close = +d.close;
    d.open = +d.open;
});
*/
// Class for the model
// to create an object: new GraphData(a,b)
function NetworkDataClass(nodes, links){
    this.nodes = nodes;
    this.links = links;
    this.modefied = false;
}

var networkData;  // model data
var nodes, links, force;
var path, circle, svg, drag_line;
// This var belongs to the model not the view
var weightCutoff = 0.01; // show edges with weight greater than this value

var CONST = {
        r: 20, // radius of nodes
        arrowLength: 150, // Arrow length
        width: 2800, //mainContentsWidth - 20, // svg width
        height: 2800, //800, // svg height
        nodeEditingEnabled: false, // enable add/delete nodes
        activateColor: '#006600',
        inhibitorColor: '#A00000',
        baseStrokeWidth: 1,
        varStrokeWidth: 2//1.6
    };

// Node Colors
var colors = d3.scale.category20();
var nodeColor = d3.rgb(174, 199, 232);
var nodeColorSelected = d3.rgb(200, 199, 232);
var lastNodeId = 0;     // TODO: need redesign (not maintained for customGraph)

// only respond once per keydown
var lastKeyDown = -1;


drawGraph();

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// mouse event vars, works also if indise drawGraph
var selected_node = null,
    selected_link = null,
    selected_weight = null,
    mousedown_link = null,
    mousedown_node = null,
    mousedown_weight = null,
    mouseup_node = null;
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function resetMouseVars() {
    mousedown_node = null;
    mouseup_node = null;
    mousedown_link = null;
    mousedown_weight = null;
}
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// Called by the form that will change the value of the selected 
// edge weight
// >>>>>>>>>>>>>>>>>> TODO: update the networkData object
function updateWeight(newWeight){
    if (selected_weight == null)
        return;

    // update the weight of the selected_weight text??
    var text = d3.select(selected_weight);
    text.text(newWeight);
}  
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// redraw current graph if exist
function redrawGraph(wCutoff){
    if (force == undefined) return;

    if (wCutoff != undefined){
        weightCutoff = wCutoff;
        links = getUpdatedLinks();
    }
    // unfix positions       
    d3.selectAll('.node').classed("fixed", function(d){d.fixed = false});
    
    //restart(true); // don't update force
    restart(false); // work around
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// update edges of current graph if exist
function updateEdges(wCutoff){
    if (force == undefined) return;

    if (wCutoff != undefined){
        weightCutoff = wCutoff;
        links = getUpdatedLinks();
    }
    // unfix positions       
    //d3.selectAll('.node').classed("fixed", function(d){d.fixed = false});
    
    //restart(true); // don't update force
    restart(false); // work around
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function initVariables(){
    path = null, circle = null, svg = null, drag_line = null;
    resetMouseVars();
    // This var belongs to the model not the view
    weightCutoff = 0.01; // show edges with weight greater than this value 
    $('#weightCutoffSlider').slider('setValue', weightCutoff);
}

// Inistial drawing of the graph
function drawGraph(customGraph) {
   
    var mainContentsWidth = parseInt(d3.select("#mainContents").style("width"));
    var mainContentsHeight = parseInt(d3.select("#mainContents").style("height"));

    // clear  variables.
    initVariables();
    
    d3.select('#svgDisplay').html(''); // clear svg
    

    svg = d3.select('#svgDisplay')
        .append('svg')
        .attr('width', CONST.width)
        .attr('height', CONST.height);

    $('#svgDisplay').parent().scrollLeft((CONST.width-mainContentsWidth)/2);
    $('#svgDisplay').parent().scrollTop((CONST.height-600)/2);

    // set up initial nodes and links
    //  - nodes are known by 'id', not by index in array.
    //  - reflexive edges are indicated on the node (as a bold black circle).
    //  - links are always source < target; edge directions are set by 'left' and 'right'.
    nodes = [
        {
        id: 'ABC',
        reflexive: false,
        target: [2, 3],
        weights: [.6, .8]
    }, {
        id: 'XYZ',
        reflexive: true,
        target: [4, 2],
        weights: [.4, .9]
    }, {
        id: 'id3',
        reflexive: false,
        target: [4],
        weights: [.2, .5]
    }, {
        id: 'ww3',
        reflexive: false
    }, {
        id: 'API',
        reflexive: true
    }
    ];

    lastNodeId = 4;
    //  links = [
    //    {source: nodes[0], target: nodes[1], left: false, right: true },
    //    {source: nodes[1], target: nodes[2], left: false, right: true }
    //  ];

    //~~~~~~~~ Moved to main ? ~~~~~~~~~~/
    
    //////////var links;
    console.log("Drawing graph: "+ customGraph);
    if (customGraph == undefined) {
        links = getD3Links(nodes);
    } else {
        nodes = [];
        links = customGraph;       
        var nodeNames = [];
        // get all nodes names
        links.map(function(link) {
            nodeNames.push(link['source']);
            nodeNames.push(link['target']);
        });
        //console.dir(nodeNames);
        // get uinque names
        var uniqueNames = nodeNames.filter(function(item, i, ar) {
            return ar.indexOf(item) === i;
        });
        for (var i in uniqueNames) {
            nodes[i] = {
                id: uniqueNames[i],
                reflexive: false
            };
        }
        for (var i in links) {
            links[i].target = nodes[uniqueNames.indexOf(links[i].target)]; // link to the object instead of index (TOBE changed)
            links[i].source = nodes[uniqueNames.indexOf(links[i].source)]; // link to the object instead of index (TOBE changed)
            links[i].weight = links[i].weight; // / 100.0;
            links[i].left = false;
            links[i].right = true;
        }
    }

    console.log("Nodes:");
    console.dir(nodes);
    console.log("Links:");
    console.dir(links);

    // object containing the model
    networkData = new NetworkDataClass(nodes, links);

    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    //               Draw Graph 
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    // ----------------- init D3 force layout ------------------
    force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([CONST.width, CONST.height])
        //.linkDistance(CONST.arrowLength)
        //.charge(-500)

    .linkStrength(0.9) // best
        .friction(0.9) // velocity decay: at each tick of the simulation
        .linkDistance(150)
        .charge(-700)
        .gravity(0.2) // gravity is implemented as a weak geometric constraint similar to a virtual spring connecting each node to the center of the layout's size
    .on("tick", tick)
    .on('start', start);
 
    // fix nodes positions
    fixPos();

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
    // fix positions after first force ends
    force.on('end', function() {
        // fix positions       
        d3.selectAll('.node').classed("fixed", function(d){d.fixed = true});
    });
    
    // local to marker adjustment
    var arrowWidth = 12,
        arrowHeight = 7;

    // define arrow markers for graph links
    // The <defs> element normally holds a set of reusable definitions for the SVG image.
    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow-Activator')
        .attr('viewBox', '0 -' + arrowWidth / 2 + ' ' + arrowHeight + ' ' + arrowWidth) // minx, miny, width, height
        //.attr('viewbox', '0 -5 ')
        .attr('refX', arrowHeight / 2) // approximate, works well if marker is an Equilateral Triangle
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-' + arrowWidth / 2 + ' L' + arrowHeight + ',0 L0, ' + arrowWidth / 2 + ' Z') // mini-lang of how to move the pen over the paper
        // .attr('d', 'M0,-7 L10,0 L0,7 Z')
        .classed('marker', true);

    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'start-arrow-Activator')
        .attr('viewBox', '0 -' + arrowWidth / 2 + ' ' + arrowHeight + ' ' + arrowWidth) // minx, miny, width, height
        .attr('refX', arrowHeight / 2) //
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M' + arrowHeight + ',-' + arrowWidth / 2 + ' L0,0 L' + arrowHeight + ',' + arrowWidth / 2 + ' Z') // mini-lang of how to move the pen over the paper
        //.attr('d', 'M10,-5 L0,0 L10,5 Z')
        .classed('marker', true);

    // Inhibitor markers
    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow-Inhibitor')
        .attr('viewBox', '0 -' + arrowWidth / 2 + ' ' + arrowHeight + ' ' + arrowWidth) // minx, miny, width, height
        //.attr('viewbox', '0 -5 ')
        .attr('refX', arrowHeight / 2) // approximate, works well if marker is an Equilateral Triangle
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M3,-' + arrowWidth / 2 + ' L3, ' + arrowWidth / 2 + ' Z') // mini-lang of how to move the pen over the paper
        .classed('marker', true);

    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'start-arrow-Inhibitor')
        .attr('viewBox', '0 -' + arrowWidth / 2 + ' ' + arrowHeight + ' ' + arrowWidth) // minx, miny, width, height
        //.attr('viewbox', '0 -5 ')
        .attr('refX', arrowHeight / 2) // approximate, works well if marker is an Equilateral Triangle
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M3,-' + arrowWidth / 2 + ' L3, ' + arrowWidth / 2 + ' Z') // mini-lang of how to move the pen over the paper
        .classed('marker', true);



    // line displayed when dragging new nodes
    // var drag_line = svg.append('svg:path')
    drag_line = svg.append('svg:path')
        .attr('class', 'link dragline hidden')
        .attr('d', 'M0,0 L0,0');

    // handles to link and node element groups
    // var path = svg.append('svg:g').selectAll('.link'),
    path = svg.append('svg:g').selectAll('.link');
    //var circle = svg.append('svg:g').selectAll('.node');
    circle = svg.append('svg:g').selectAll('.node');

    
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    //============================================================//
    //               app starts here                              //
    //------------------------------------------------------------//

    svg .on('mousedown', addNode)
        .on('mousemove', mousemove)
        .on('mouseup', mouseup);

    d3.select(window)
        .on('keydown', keydown)
        .on('keyup', keyup);

    restart();
} // drawGraph(customGraph)
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


//=====================================================================
//                   D3 display functions
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// add the curvy lines
function tick() {
//     path.attr("d", function(d) {
//         var dx = d.target.x - d.source.x,
//             dy = d.target.y - d.source.y,
//             dr = Math.sqrt(dx * dx + dy * dy);
//         return "M" +
//             d.source.x + "," +
//             d.source.y + "A" +
//             dr + "," + dr + " 0 0,1 " +
//             d.target.x + "," +
//             d.target.y;
//     });
//
//     circle
//         .attr("transform", function(d) {
//   	    return "translate(" + d.x + "," + d.y + ")"; });
}

// Skip some rendering between ticks to speedup view
function start(){
    var ticksPerRender = 2;
    requestAnimationFrame(function render() {
        for (var i = 0; i < ticksPerRender; i++) {
            force.tick();
        }
        updatePositions();
      
        if (force.alpha() > 0) {
            requestAnimationFrame(render);
        }
    });
}
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// update force layout (called when needed by start event)
function updatePositions() {
    // draw directed edges (links) with proper padding from node centers
    path.selectAll('path').attr('d', function(d) {
        var deltaX = d.target.x - d.source.x,
            deltaY = d.target.y - d.source.y,
            dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
            normX = deltaX / dist,
            normY = deltaY / dist,
            sourcePadding = d.left ? CONST.r + 5 : CONST.r,
            targetPadding = d.right ? CONST.r + 5 : CONST.r,
            sourceX = d.source.x + (sourcePadding * normX),
            sourceY = d.source.y + (sourcePadding * normY),
            targetX = d.target.x - (targetPadding * normX),
            targetY = d.target.y - (targetPadding * normY);
        return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
    });

    circle.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    });

    // // Fix the direction of the edge label
    path.selectAll("text")
        .attr('transform', function(d, i) {
            if (d.target.x < d.source.x) {
                bbox = this.getBBox();
                rx = bbox.x + bbox.width / 2;
                ry = bbox.y + bbox.height / 2;
                return 'rotate(180 ' + rx + ' ' + ry + ')';
            } else {
                return 'rotate(0)';
            }
        });

} //end tick()

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// update graph (called when needed)
function restart(noForceStart) {
    console.time('restart');
    console.log("restat is called...");

    // II- Circle (node) group
    // NB: the function arg is crucial here! nodes are known by id, not by index!
    circle = circle.data(nodes, function(d) {return d.id;});

    // update existing nodes (reflexive & selected visual states)
    circle.selectAll('circle')
        //.style('fill', function(d) { return (d === selected_node) ? d3.rgb(colors(d.id)).brighter().toString() : colors(d.id); })
        .style('fill', function(d) {return (d === selected_node) ? nodeColorSelected : nodeColor;})
        .classed('reflexive', function(d) {return d.reflexive;})
        .classed('selected', function(d) {return d === selected_node;});

    var g = circle.enter()
        .append('svg:g')
        .attr('class', 'node');

    g.append('svg:circle')
    //g.append('svg:ellipse')
        .attr('class', 'node')
       //.attr('rx', CONST.r+5)
       //.attr('ry', CONST.r-5)
        .attr('r', CONST.r)
        //.style('fill', function(d) { return (d === selected_node) ? nodeColor.brighter().toString() : nodeColor; })
        .style('fill', function(d) {return (d === selected_node) ? nodeColorSelected : nodeColor;})
        //.style('stroke', function(d) { return nodeColor.darker().toString(); })
        .style('stroke', function(d) {return nodeColor;})
        .classed('reflexive', function(d) {return d.reflexive;})
        .on('mouseover', function(d) {
            if (!mousedown_node || d === mousedown_node) return;
            // enlarge target node
            d3.select(this).attr('transform', 'scale(1.2)');
        })
        .on('mouseout', function(d) {
            if (!mousedown_node || d === mousedown_node) return;
            // unenlarge target node
            d3.select(this).attr('transform', '');
        })
        .on('mousedown', function(d) {
            if (d3.event.ctrlKey) return;

            // select node
            mousedown_node = d;
            if (mousedown_node === selected_node) selected_node = null;
            else selected_node = mousedown_node;
            selected_link = null;

            // reposition drag line
            drag_line
                .style('marker-end', 'url(#end-arrow-Acrivator)')
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);

            restart(true);
        })
        .on('mouseup', function(d) {
            if (!mousedown_node) return;

            // needed by FF
            drag_line
                .classed('hidden', true)
                .style('marker-end', '');

            // check for drag-to-self
            mouseup_node = d;
            if (mouseup_node === mousedown_node) {
                resetMouseVars();
                return;
            }

            // unenlarge target node
            d3.select(this).attr('transform', '');

            // add link to graph (update if exists)
            // NB: links are strictly source < target; arrows separately specified by booleans
            var source, target, direction;
            if (mousedown_node.id < mouseup_node.id) {
                source = mousedown_node;
                target = mouseup_node;
                direction = 'right';
            } else {
                source = mouseup_node;
                target = mousedown_node;
                direction = 'left';
            }

            // search if the link already exist
            var link;
            link = links.filter(function(l) {
                return (l.source === source && l.target === target);
            })[0];

            if (link) {
                link[direction] = true;
            } else {
                link = {
                    source: source,
                    target: target,
                    left: false,
                    right: false,
                    weight: 0.5
                };
                link[direction] = true;
                links.push(link);
            }

            // select new link
            selected_link = link;
            selected_node = null;
            restart(false);
        }); // end circle (node)

    // show node IDs
    g.append('svg:text')
        .attr('x', 0)
        .attr('y', 4) ////////////////////////////////////////
        .attr('class', 'id')
        .text(function(d) {
            return d.id;
        });

    // remove old nodes
    circle.exit().remove();


    //-------------------------------------------------------

    // I- path (link) group
    // bind path with data and return 3 types of selectors
    path = path.data(links, function(d, i) { 
        // console.log('d is: ');
        // console.dir(d);
        // console.log('current link: '+ d.source.id+'-'+d.target.id);
        return(d.source.id+'-'+d.target.id); 
    });

    // update existing links (selectors 1: existing elements in data)
    path.selectAll('path.link')            
        // update for bi-directional edge
        // .style('marker-start', function(d) {return d.left ? 'url(#start-arrow)' : '';})
        // .style('marker-end', function(d) {return d.right ? 'url(#end-arrow)' : '';}); 
 //       .filter(function(d){return isWeightCutOff(d);}) // don't show link below cutoff
        .classed('selected', function(d) {return d === selected_link;})
        .style('stroke-width', function(d){
                return CONST.baseStrokeWidth +
                       Math.abs(CONST.varStrokeWidth * d.weight)+'px';})
        .style('marker-start', function(d){return getArrowType(d, 'start');})
        .style('marker-end', function(d){return getArrowType(d, 'end');});

    
    var gpath = path.enter()
        .append('svg:g')
        .attr('id', function(d, i) {return 'linkGroup_'+d.source.id+'-'+d.target.id})
        .attr('class', 'link');

    // add new links (selectors 2: new elements in data)
    gpath.append('svg:path')
 //       .filter(function(d){return isWeightCutOff(d);}) // don't show link below cutoff
        .attr('class', 'link')
        .attr('id', function(d, i) {return 'edgepath_'+d.source.id+'-'+d.target.id})
        .style('stroke', function(d) {if (d.weight > 0) {return CONST.activateColor;}
                                      else return CONST.inhibitorColor;
                                    })
        //.style('marker-start', function(d) {return d.left ? 'url(#start-arrow)' : '';})
        //.style('marker-end', function(d) {return d.right ? 'url(#end-arrow)' : '';});            
        .classed('selected', function(d) {return d === selected_link;})
        .style('stroke-width', function(d){
                    return  CONST.baseStrokeWidth +
                            Math.abs(CONST.varStrokeWidth * d.weight)+'px';})
        .style('marker-start', function(d){return getArrowType(d, 'start');})
        .style('marker-end', function(d){return getArrowType(d, 'end');});


    // Hidden thick line, to catch mouse clicks
    gpath.append('svg:path')
 //       .filter(function(d){return isWeightCutOff(d);}) // don't show link below cutoff
        .attr('class', 'hiddenLink')
        .on('mousedown', function(d) {
            if(d3.event.ctrlKey) return;
            // select link
            mousedown_link = d;
            if (mousedown_link === selected_link) selected_link = null;
            else selected_link = mousedown_link;
            selected_node = null;

            console.log("links before Selection:");
            console.log(links);

            restart(true);
        });


    var edgelabels = gpath.append('text')
        .attr('class', 'edgeText')            
        .attr('dy', -5);

    edgelabels.append('textPath')
        .attr('id', function(d, i) {return 'weight_'+d.source.id+'-'+d.target.id})
        .attr('xlink:href', function(d, i) {return '#edgepath_'+d.source.id+'-'+d.target.id})
        .attr('startOffset', "50%") // Here not in css      
        .text(function(d, i) {
            return Math.round(d.weight * 100) / 100; // round to two decimal digits
            //return d.weight;
        })
        .on('dblclick', function(d, i) {                
            var text = d3.select(this);
            selected_weight = this;
            var newText = parseFloat(text.text());
            // var newText = (parseFloat(text.text()) + 0.2) % 1.0;
            //newText = Math.round(newText * 100) / 100; // round to two decimal digits
            //text.text(newText);
            // reset node or edge selection, & redraw
            selected_node = null;
            selected_link = null;
            restart(false);
            // show dialog box
            showTextBox(newText);
        });

    // remove old links (selectors 3: for elements that already exist but not in path.data(link))
    path.exit()
        .remove();


    //------------------------------------------

    // set the graph in motion, unless noForceStart=true
    if (!noForceStart) {
        force.start();
    }
    
    // console.trace();
    console.timeEnd('restart');

} // end restart




// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
//~~~~~~~~~~~~~~~~ Mouse events ~~~~~~~~~~~~~~~~~~~~~~~~~//

function mousemove() {
    if (!mousedown_node) return;

    // update drag line
    drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);

    /////////////////restart();
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function mouseup(e) {   
    if (isRightClick(e)){
        ////alert("right click");
        return;
    }    
    if (mousedown_node) {
        // hide drag line
        drag_line
            .classed('hidden', true)
            .style('marker-end', '');
    }

    // because :active only works in WebKit?
    svg.classed('active', false);

    // clear mouse event vars
    resetMouseVars();
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function spliceLinksForNode(node) {
    var toSplice = links.filter(function(l) {
        return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
        links.splice(links.indexOf(l), 1);
    });
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function keydown() {

    if (lastKeyDown !== -1) return;
    lastKeyDown = d3.event.keyCode;

    // ctrl
    if (d3.event.keyCode === 17) {
        circle.call(force.drag); //// enabling dragging of nodes
        circle.call(fixPos); // fixing node positions
        svg.classed('ctrl', true);
    }

    if (!selected_node && !selected_link) return;
    switch (d3.event.keyCode) {
        case 8: // backspace
        case 46: // delete
            deleteObject();
            break;
        case 66: // B
            if (selected_link) {
                // set link direction to both left and right
                selected_link.left = true;
                selected_link.right = true;
            }
            restart();
            break;
        case 76: // L
            if (selected_link) {
                // set link direction to left only
                selected_link.left = true;
                selected_link.right = false;
            }
            restart();
            break;
        case 82: // R
            if (selected_node) {
                // toggle node reflexivity
                selected_node.reflexive = !selected_node.reflexive;
            } else if (selected_link) {
                // set link direction to right only
                selected_link.left = false;
                selected_link.right = true;
            }
            restart();
            d3.event.preventDefault();
            break;
    }
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function keyup() {
    lastKeyDown = -1;

    // ctrl
    if (d3.event.keyCode === 17) {
        circle.on('mousedown.drag', null) // old: fix position after ctrl+drag (wrong solution)?
        circle.on('touchstart.drag', null); // works in fixing position forever?
        svg.classed('ctrl', false);
    }
}

function fixPos(){
    force.drag()
        .on("dragstart", function dragstart(d) {
            d3.select(this).classed("fixed", d.fixed = true); //Works: fixes position of a node:)))))
        });
}

//=====================   Util functions  =========================//

// function to get D3 formated links array 
function getD3Links(nodes) {
    var links = [];
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].target !== undefined) {
            for (var x = 0; x < nodes[i].target.length; x++) {
                links.push({
                    source: nodes[i],
                    target: nodes[nodes[i].target[x]],
                    weight: nodes[i].weights[x],
                    left: false,
                    right: true
                })
            }
        }
    }
    return links;
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function getArrowType(data, direction){       
    // For start arrow       
    if (direction=='start' && data.left){
        if (data.weight > 0) 
            return 'url(#start-arrow-Activator)';
        else
            return 'url(#start-arrow-Inhibitor)';
    } // for end arrow
    else if (direction=='end' && data.right){
        if (data.weight > 0) 
            return 'url(#end-arrow-Activator)';
        else
            return 'url(#end-arrow-Inhibitor)';
    }
    return '';        
}
    
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
var generateRandomID = function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

/**
 *
 * @param {string} msg
 * @param {string} type: info, error,
 * @returns {msg}
 */
var showMsg = function(msg, type) {
    // defaulr type is info
    if (type === undefined) {
        type = 'info';
    }
    Messenger().post({
        message: msg,
        type: type,
        hideAfter: 3,
        showCloseButton: true
    });
};

/** Return true if the weight of the link is greater than the cutoff
**/
function isWeightCutOff(link){
    console.log("weight cutoff applied is: "+weightCutoff);

    if (Math.abs(link.weight) > weightCutoff)
        return true; // edge will be included
    else return false; // edge will be excluded
                        
}

//==================================================================//
//==================== New functions ===============================//

function addNode() {

    if (!CONST.nodeEditingEnabled)
        return;
    // prevent I-bar on drag
    //d3.event.preventDefault();

    // because :active only works in WebKit?
    svg.classed('active', true);

    if (d3.event.ctrlKey || mousedown_node || mousedown_link) return;

    // insert new node at point
    var point = d3.mouse(this),
        node = {
            id: 'ID' + ++lastNodeId,
            reflexive: false
        };
    node.x = point[0];
    node.y = point[1];
    nodes.push(node);

    showMsg('New node is added', 'success');
    restart();
}

// TODO: update networkData >>>>>>>>>>>>>>
function deleteObject() {
    if (selected_node && CONST.nodeEditingEnabled) {
        nodes.splice(nodes.indexOf(selected_node), 1);
        spliceLinksForNode(selected_node);
        showMsg('Node is deleted');
        selected_node = null;
    }

    else if (selected_link) {
        console.log(selected_link);
        console.log('index of selected_link: ' + links.indexOf(selected_link));
        links.splice(links.indexOf(selected_link), 1);
        console.log("links after deletion:");
        console.log(links);
        showMsg('Edge is deleted');
        selected_link = null;
    }

    restart(); // restart(true);  //restart without moving the graph, not working!!!
}

//====================================================================
//                  Data handling
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// return the links from the model that are above the cut-off
function getUpdatedLinks(){
    var links = [];

    console.log("Applying cutoff: "+weightCutoff);

    for (i in networkData.links){   // iterate over index
        console.log(networkData.links[i]);
        if (Math.abs(networkData.links[i].weight) > weightCutoff){
            console.log("Adding the link.");
            links.push(networkData.links[i]);
        }
        else{
            
        }
    }
    return links;
}