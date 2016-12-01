// Testing D3 SVG

(function(){
    var mainContentsWidth = parseInt(d3.select("#mainContents").style("width"));

    var CONST = {
        r: 18,                          // radius of nodes
        arrowLength: 150,               // Arrow length
        width: mainContentsWidth-20,    // svg width
        height: 700,                    // svg height
        nodeEditingEnabled: false       // enable add/delete nodes
    };

    // Node Colors
    var colors = d3.scale.category20();
    var nodeColor = d3.rgb(174, 199, 232);
    var nodeColorSelected = d3.rgb(200, 199, 232);

    d3.select('#testDisplay').html(''); // clear svg
    var svg = d3.select('#testDisplay')
      .append('svg')
      .attr('width', CONST.width)
      .attr('height', CONST.height);

    // set up initial nodes and links
    //  - nodes are known by 'id', not by index in array.
    //  - reflexive edges are indicated on the node (as a bold black circle).
    //  - links are always source < target; edge directions are set by 'left' and 'right'.
    var nodes = [
        {id: 'ABC', reflexive: false,  target:[2,3]},
        {id: 'XYZ', reflexive: true,  target:[4,2]},
        {id: 'id3', reflexive: false,  target:[4]},
        {id: 'ww3', reflexive: false},
        {id: 'API', reflexive: true}
    ];
    var lastNodeId = 4;
    //  links = [
    //    {source: nodes[0], target: nodes[1], left: false, right: true },
    //    {source: nodes[1], target: nodes[2], left: false, right: true }
    //  ];

    //~~~~~~~~ Moved to main ? ~~~~~~~~~~/
    var links;
    links = getD3Links(nodes);
    
    console.log("Nodes:");
    console.dir(nodes);
    console.log("Links:");
    console.dir(links);

    
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    //               Draw Graph 
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    // init D3 force layout
    var force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([CONST.width, CONST.height])
        //.linkDistance(CONST.arrowLength)
        //.charge(-500)

        .linkStrength(0.9)  // best
        .friction(0.9)      // velocity decay: at each tick of the simulation
        .linkDistance(170)
        .charge(-700)
        .gravity(0.2)   // gravity is implemented as a weak geometric constraint similar to a virtual spring connecting each node to the center of the layout's size

        .on('tick', tick);

    var fixPos = force.drag()
       .on("dragstart", function dragstart(d) {
           d3.select(this).classed("fixed", d.fixed = true); //Works: fixes position of a node:)))))
    });

    // local to marker adjustment
    var arrowWidth = 12, arrowHeight = 7;

    // define arrow markers for graph links
    // The <defs> element normally holds a set of reusable definitions for the SVG image.
    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow')
        .attr('viewBox', '0 -'+arrowWidth/2+' '+arrowHeight+' '+arrowWidth)  // minx, miny, width, height
        //.attr('viewbox', '0 -5 ')
        .attr('refX', arrowHeight/2)    // approximate, works well if marker is an Equilateral Triangle
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
      .append('svg:path')
        .attr('d', 'M0,-'+arrowWidth/2+' L'+arrowHeight+',0 L0, '+arrowWidth/2+' Z')  // mini-lang of how to move the pen over the paper
       // .attr('d', 'M0,-7 L10,0 L0,7 Z')
        .classed('marker', true);

    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'start-arrow')
        .attr('viewBox', '0 -'+arrowWidth/2+' '+arrowHeight+' '+arrowWidth)  // minx, miny, width, height
        .attr('refX', arrowHeight/2) //
        .attr('markerWidth', arrowWidth)
        .attr('markerHeight', arrowHeight)
        .attr('orient', 'auto')
      .append('svg:path')
        .attr('d', 'M'+arrowHeight+',-'+arrowWidth/2+' L0,0 L'+arrowHeight+','+arrowWidth/2+' Z')  // mini-lang of how to move the pen over the paper
        //.attr('d', 'M10,-5 L0,0 L10,5 Z')
        .classed('marker', true);

    // line displayed when dragging new nodes
    var drag_line = svg.append('svg:path')
      .attr('class', 'link dragline hidden')
      .attr('d', 'M0,0 L0,0');

    // handles to link and node element groups
    var path = svg.append('svg:g').selectAll('.link'),
        circle = svg.append('svg:g').selectAll('.node');

    // mouse event vars
    var selected_node = null,
        selected_link = null,
        mousedown_link = null,
        mousedown_node = null,
        mouseup_node = null;

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    function resetMouseVars() {
      mousedown_node = null;
      mouseup_node = null;
      mousedown_link = null;
    }

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // update force layout (called automatically each iteration)
    function tick() {
      // draw directed edges (links) with proper padding from node centers
      path.selectAll('path').attr('d', function(d) {
        var deltaX = d.target.x - d.source.x,
            deltaY = d.target.y - d.source.y,
            dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
            normX = deltaX / dist,
            normY = deltaY / dist,
            sourcePadding = d.left ? CONST.r+5 : CONST.r,
            targetPadding = d.right ? CONST.r+5 : CONST.r,
            sourceX = d.source.x + (sourcePadding * normX),
            sourceY = d.source.y + (sourcePadding * normY),
            targetX = d.target.x - (targetPadding * normX),
            targetY = d.target.y - (targetPadding * normY);
        return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
      });

      circle.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
      });


      // Fix the direction of the edge label
      path.selectAll("text")
          .attr('transform',function(d,i){  
                    if (d.target.x<d.source.x){
                        bbox = this.getBBox();
                        rx = bbox.x+bbox.width/2;
                        ry = bbox.y+bbox.height/2;
                        return 'rotate(180 '+rx+' '+ry+')';
                    }
                    else {
                        return 'rotate(0)';
                    }
                });

                  
    } //end tick()

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    // update graph (called when needed)
    function restart(noForceStart) {
        console.time('restart');
      
      // II- Circle (node) group
      // NB: the function arg is crucial here! nodes are known by id, not by index!
      circle = circle.data(nodes, function(d) { return d.id; });

      // update existing nodes (reflexive & selected visual states)
      circle.selectAll('circle')
        //.style('fill', function(d) { return (d === selected_node) ? d3.rgb(colors(d.id)).brighter().toString() : colors(d.id); })
        .style('fill', function(d) { return (d === selected_node) ? nodeColorSelected : nodeColor; })
        .classed('reflexive', function(d) { return d.reflexive; })
        .classed('selected', function(d) { return d === selected_node; });


      var g = circle.enter()
                .append('svg:g')
                .attr('class', 'node');

      g.append('svg:circle')
        .attr('class', 'node')
        //.attr('fixed', true)       // fixed position, not working!
        .attr('r', CONST.r)
        //.style('fill', function(d) { return (d === selected_node) ? nodeColor.brighter().toString() : nodeColor; })
        .style('fill', function(d) { return (d === selected_node) ? nodeColorSelected : nodeColor; })
        //.style('stroke', function(d) { return nodeColor.darker().toString(); })
        .style('stroke', function(d) { return nodeColor; })
        .classed('reflexive', function(d) { return d.reflexive; })
        .on('mouseover', function(d) {
              if(!mousedown_node || d === mousedown_node) return;
              // enlarge target node
              d3.select(this).attr('transform', 'scale(1.2)');
        })
        .on('mouseout', function(d) {
              if(!mousedown_node || d === mousedown_node) return;
              // unenlarge target node
              d3.select(this).attr('transform', '');
        })
        .on('mousedown', function(d) {
              if(d3.event.ctrlKey) return;

              // select node
              mousedown_node = d;
              if(mousedown_node === selected_node) selected_node = null;
              else selected_node = mousedown_node;
              selected_link = null;

              // reposition drag line
              drag_line
                .style('marker-end', 'url(#end-arrow)')
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);

                restart(true);
        })
        .on('mouseup', function(d) {
              if(!mousedown_node) return;

              // needed by FF
              drag_line
                .classed('hidden', true)
                .style('marker-end', '');

              // check for drag-to-self
              mouseup_node = d;
              if(mouseup_node === mousedown_node) { resetMouseVars(); return; }

              // unenlarge target node
              d3.select(this).attr('transform', '');

              // add link to graph (update if exists)
              // NB: links are strictly source < target; arrows separately specified by booleans
              var source, target, direction;
              if(mousedown_node.id < mouseup_node.id) {
                source = mousedown_node;
                target = mouseup_node;
                direction = 'right';
              } else {
                source = mouseup_node;
                target = mousedown_node;
                direction = 'left';
              }

            
              var link = links.filter(function(l) {
                return (l.source === source && l.target === target);
              })[0];

              if(link) {
                link[direction] = true;
              } else {
                link = {source: source, target: target, left: false, right: false};
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
          .text(function(d) { return d.id; });

        // remove old nodes
        circle.exit().remove();


        //-------------------------------------------------------

        // I- path (link) group
      // bind path with data and return 3 types of selectors
      path = path.data(force.links());

      console.log(path);
      // update existing links (selectors 1: existing elements in data)
      path.selectAll('path')
        .classed('selected', function(d) { return d === selected_link; })
        .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; });


      var gpath = path.enter()
                .append('svg:g')
                .attr('class', 'link');

      // add new links (selectors 2: new elements in data)
      gpath.append('svg:path')
        .attr('class', 'link')
        .attr('id', function(d,i) {return 'edgepath'+i})
        .classed('selected', function(d) { return d === selected_link; })
        .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; })
        .on('mousedown', function(d) {
              if(d3.event.ctrlKey) return;
              // select link
              mousedown_link = d;
              if(mousedown_link === selected_link) selected_link = null;
              else selected_link = mousedown_link;
              selected_node = null;
              restart(true);
        });


      var edgelabels =  gpath.append('text')        
        .attr('class', 'edgeText')
        .attr('id', function(d,i){return 'weight'+i})
        .attr('dy', -5);

      edgelabels.append('textPath')
        .attr('xlink:href',function(d,i) {return '#edgepath'+i})
        .attr('startOffset', "50%")    // Here not in css      
        .text(function(d,i){
            return 0.5;
            //return d.weight;
        })
        .on('click', function(d,i) {             
            var text = d3.select(this);
            var newText = (parseFloat(text.text()) + 0.25) % 1.0;
            text.text(newText);
        });


      // remove old links (selectors 3: for elements that already exist but not in path.data(link))
      path.exit().remove();

      //------------------------------------------


        // set the graph in motion, unless noForceStart=true
        if (!noForceStart){
            force.start();
        }

        // console.trace();
        console.timeEnd('restart');

    } // end restart

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
    //~~~~~~~~~~~~~~~~ Mouse events ~~~~~~~~~~~~~~~~~~~~~~~~~//

    function mousemove() {
      if(!mousedown_node) return;

      // update drag line
      drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);

      /////////////////restart();
    }

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    function mouseup() {
      if(mousedown_node) {
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

    // only respond once per keydown
    var lastKeyDown = -1;


    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    function keydown() {

      if(lastKeyDown !== -1) return;
      lastKeyDown = d3.event.keyCode;

      // ctrl
      if(d3.event.keyCode === 17) {
        circle.call(force.drag); //// enabling dragging of nodes
        circle.call(fixPos);  // fixing node positions
        svg.classed('ctrl', true);
      }

      if(!selected_node && !selected_link) return;
      switch(d3.event.keyCode) {
        case 8: // backspace
        case 46: // delete
          deleteObject();
          break;
        case 66: // B
          if(selected_link) {
            // set link direction to both left and right
            selected_link.left = true;
            selected_link.right = true;
          }
          restart();
          break;
        case 76: // L
          if(selected_link) {
            // set link direction to left only
            selected_link.left = true;
            selected_link.right = false;
          }
          restart();
          break;
        case 82: // R
          if(selected_node) {
            // toggle node reflexivity
            selected_node.reflexive = !selected_node.reflexive;
          } else if(selected_link) {
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
      if(d3.event.keyCode === 17) {
        circle.on('mousedown.drag', null) // old: fix position after ctrl+drag (wrong solution)?
        circle.on('touchstart.drag', null); // works in fixing position forever?
        svg.classed('ctrl', false);
      }
    }

    //=====================   Util functions  =========================//

    // function to get D3 formated links array 
    function getD3Links(nodes) {
        var links = [];
        for (var i = 0; i< nodes.length; i++) {
              if (nodes[i].target !== undefined) {
                    for (var x = 0; x< nodes[i].target.length; x++ ) {
                          links.push({
                                source: nodes[i],
                                target: nodes[nodes[i].target[x]],
                                // weight: nodes[i].weight[i] // think how to store weight in adj list
                                left: false,
                                right: true
                          })
                    }
              }
        }
        return links;
    }

    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    var generateRandomID = function () {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
          return v.toString(16);
        });
    };

    /**
     *
     * @param {string} msg
     * @param {string} type: info, error,
     * @returns {msg}
     */
    var showMsg = function(msg, type){
        // defaulr type is info
        if (type === undefined){
            type = 'info';
        }
        Messenger().post({
                message: msg,
                type: type,
                hideAfter: 3,
                showCloseButton: true
        });
    };
  

    //==================================================================//
    //==================== New functions ===============================//

    function addNode(){

      if (!CONST.nodeEditingEnabled)
        return;
      // prevent I-bar on drag
      //d3.event.preventDefault();

      // because :active only works in WebKit?
      svg.classed('active', true);

      if(d3.event.ctrlKey || mousedown_node || mousedown_link) return;

      // insert new node at point
      var point = d3.mouse(this),
          node = {id: 'ID' + ++lastNodeId, reflexive: false};
      node.x = point[0];
      node.y = point[1];
      nodes.push(node);

      showMsg('New node is added', 'success');
      restart();
    }


    function deleteObject(){
        if(selected_node && CONST.nodeEditingEnabled) {
            nodes.splice(nodes.indexOf(selected_node), 1);
            spliceLinksForNode(selected_node);
            showMsg('Node is deleted');
            selected_node = null;
        } else if(selected_link) {
            links.splice(links.indexOf(selected_link), 1);
            showMsg('Edge is deleted');
            selected_link = null;
         }

        restart();    // restart(true);  //restart without moving the graph, not working!!!
    }

    //============================================================//
    //               app starts here                              //
    //------------------------------------------------------------//
    
    svg
      .on('mousedown', addNode)
      .on('mousemove', mousemove)
      .on('mouseup', mouseup);
    d3.select(window)
      .on('keydown', keydown)
      .on('keyup', keyup);
    restart();

})();// function()



//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//(function () {
//
//    var w = parseInt(d3.select("#mainContents").style("width"));
//
//	var width = w,
//	    height = 600;
//
//	var color = d3.scale.category20();
//
//	var moleculeExamples = {};
//
//	var radius = d3.scale.sqrt()
//	    .range([0, 6]);
//
//	var selectionGlove = glow("selectionGlove").rgb("#0000A0").stdDeviation(7);
//	var atomSelected;
//	var atomClicked = function (dataPoint) {
//	 	if (dataPoint.symbol === "H")
//	 		return;
//
//	 	if (atomSelected)
//	 		atomSelected.style("filter", "");
//
//	 	atomSelected = d3.select(this)
//	 					.select("circle")
//	 					.style("filter", "url(#selectionGlove)");
//	};
//
//	var bondSelected;
//	var bondClicked = function (dataPoint) {
//	 	Messenger().post({
//				  message: 'New Bond Selected',
//				  type: 'info',
//				  hideAfter: 3,
//				  showCloseButton: true
//				});
//
//	 	if (bondSelected)
//	 		bondSelected.style("filter", "");
//
//	 	bondSelected = d3.select(this)
//	 					.select("line")
//	 					.style("filter", "url(#selectionGlove)");
//	};
//
//	var generateRandomID = function () {
//		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
//		  var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
//		  return v.toString(16);
//		});
//	}
//
//	var svg = d3.select("#moleculeDisplay").append("svg")
//	    .attr("width", width)
//	    .attr("height", height)
//	    .call(selectionGlove);
//
//  var getRandomInt = function (min, max) {
//	  return Math.floor(Math.random() * (max - min + 1) + min);
//	}
//
//	window.loadMolecule = function () {
//	  	vex.dialog.open({
//				message: 'Copy your saved molecule data:',
//				input: "Molecule: <br/>\n<textarea id=\"molecule\" name=\"molecule\" value=\"\" style=\"height:150px\" placeholder=\"Saved Molecule Data\" required></textarea>",
//				buttons: [
//					$.extend({}, vex.dialog.buttons.YES, {
//					text: 'Load'
//				}), $.extend({}, vex.dialog.buttons.NO, {
//					text: 'Cancel'
//				})
//				],
//				callback: function(data) {
//					if (data !== false) {
//
//						newMoleculeSimulation(JSON.parse(data.molecule));
//					}
//				}
//			});
//	};
//
//	var newMoleculeSimulation = function (newMolecule, example) {
//		// Might be super dirty, but it works!
//		$('#moleculeDisplay').empty();
//		svg = d3.select("#moleculeDisplay").append("svg")
//				    .attr("width", width)
//				    .attr("height", height)
//				    .call(selectionGlove);
//		if (example)
//			newMolecule = newMolecule[example];
//		newMolecule = $.extend(true, {}, newMolecule);
//		orgoShmorgo(newMolecule);
//
//		Messenger().post({
//		  message: 'New Molecule Loaded',
//		  type: 'success',
//		  showCloseButton: true,
//		  hideAfter: 2
//		});
//	};
//
//	window.loadMoleculeExample = function () {
//		newMoleculeSimulation (moleculeExamples, $('#moleculeExample').val().trim());
//	};
//
//	$.getJSON("data/molecules.json", function(json) {
//    moleculeExamples = json;
//    newMoleculeSimulation (moleculeExamples, '2-amino-propanoic_acid');
//	});
//
//	var orgoShmorgo = function(graph) {
//	  var nodesList, linksList;
//	  nodesList = graph.nodes;
//	  linksList = graph.links;
//
//
//	  var force = d3.layout.force()
//                    .nodes(nodesList)
//                    .links(linksList)
//                    .size([width, height])
//                    .charge(-400)
//                    .linkStrength(function (d) { return d.bondType * 1;})
//                    .linkDistance(function(d) { return radius(d.source.size) + radius(d.target.size) + 20; })
//                    .on("tick", tick);
//
//	  var links = force.links(),
//	  		nodes = force.nodes(),
//	  		link = svg.selectAll(".link"),
//	  		node = svg.selectAll(".node");
//
//	  buildMolecule();
//
//	  function buildMolecule () {
//	  	// Update link data
//	  	link = link.data(links, function (d) {return d.id; });
//
//		  // Create new links
//		  link.enter().insert("g", ".node")
//		      .attr("class", "link")
//		      .each(function(d) {
//		      	// Add bond line
//		      	d3.select(this)
//		      		.append("line")
//							.style("stroke-width", function(d) { return (d.bondType * 3 - 2) * 2 + "px"; });
//
//						// If double add second line
//						d3.select(this)
//							.filter(function(d) { return d.bondType >= 2; }).append("line")
//							.style("stroke-width", function(d) { return (d.bondType * 2 - 2) * 2 + "px"; })
//							.attr("class", "double");
//
//						d3.select(this)
//							.filter(function(d) { return d.bondType === 3; }).append("line")
//							.attr("class", "triple");
//
//						// Give bond the power to be selected
//						d3.select(this)
//							.on("click", bondClicked);
//		      });
//
//		  // Delete removed links
//		  link.exit().remove();
//
//		  // Update node data
//	  	node = node.data(nodes, function (d) {return d.id; });
//
//	    // Create new nodes
//		  node.enter().append("g")
//		      .attr("class", "node")
//		      .each(function(d) {
//		      	// Add node circle
//			      d3.select(this)
//			      	.append("circle")
//		      		.attr("r", function(d) { return radius(d.size); })
//		      		.style("fill", function(d) { return color(d.symbol); });
//
//		        // Add atom symbol
//			      d3.select(this)
//			      	.append("text")
//							.attr("dy", ".35em")
//							.attr("text-anchor", "middle")
//							.text(function(d) { return d.symbol; });
//
//						// Give atom the power to be selected
//						d3.select(this)
//							.on("click", atomClicked);
//
//						// Grant atom the power of gravity
//						d3.select(this)
//							.call(force.drag);
//			    });
//
//		  // Delete removed nodes
//	    node.exit().remove();
//
//		  force.start();
//	  }
//
//	  window.saveMolecule = function () {
//	  	var specialLinks = [], specialNodes = [], nodeIdArr = [];
//	  	for (var i = nodes.length - 1; i >=0; i--) {
//	  		specialNodes.push({
//	  				symbol: nodes[i].symbol,
//						size: nodes[i].size,
//						x: nodes[i].x,
//						y: nodes[i].y,
//						id: nodes[i].id,
//						bonds: nodes[i].bonds
//					});
//	  		nodeIdArr.push(nodes[i].id);
//	  	}
//	  	for (var i = links.length - 1; i >=0; i--) {
//	  		specialLinks.push({
//						source: nodeIdArr.indexOf(links[i].source.id),
//						target: nodeIdArr.indexOf(links[i].target.id),
//						id: links[i].id,
//						bondType: links[i].bondType
//					});
//	  	}
//	  	molecule = {
//			    nodes: specialNodes,
//			    links: specialLinks
//			};
//	  	vex.dialog.open({
//				message: 'To save your current molecule, copy the data below. Next time you visit click on the load molecule and input your saved data:',
//				input: "Molecule: <br/>\n<textarea id=\"atoms\" name=\"atoms\" value=\"\" style=\"height:150px\" placeholder=\"Molecule Data\">" + JSON.stringify(molecule) + "</textarea>",
//				buttons: [
//					$.extend({}, vex.dialog.buttons.YES, {
//						text: 'Ok'
//					})
//				],
//				callback: function(data) {}
//			});
//	  };
//
//	  window.changeBond = function (newBondType) {
//	  	if (!bondSelected) {
//				Messenger().post({
//				  message: 'No Bond Selected',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//			}
//	  	var bondData = getAtomData(bondSelected);
//	  	var changeInCharge = newBondType - bondData.bondType;
//	  	var bondChangePossible = function (bond) {
//	  		return (bond.target.bonds + changeInCharge <= atomDB[bond.target.symbol].lonePairs && bond.source.bonds + changeInCharge <= atomDB[bond.source.symbol].lonePairs);
//	  	};
//
//	  	if (!newBondType || newBondType < 1 || newBondType > 3) {
//	  		Messenger().post({
//				  message: 'Internal error :(',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//	  	}
//			else if (!bondChangePossible(bondData, newBondType)) {
//				Messenger().post({
//				  message: 'That type of bond cannot exist there!',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//			}
//
//			for (var i = links.length - 1; i >= 0; i--) {
//				if (links[i].id === bondData.id) {
//					var changeInCharge = newBondType - bondData.bondType;
//					var source = retriveAtom(links[i].source.id),
//							target = retriveAtom(links[i].target.id);
//					if (changeInCharge === 2) {
//						removeHydrogen(source);
//						removeHydrogen(source);
//						removeHydrogen(target);
//						removeHydrogen(target);
//					}
//					else if (changeInCharge === 1) {
//						removeHydrogen(source);
//						removeHydrogen(target);
//					}
//					else if (changeInCharge === -1) {
//						addHydrogens(source, 1);
//						addHydrogens(target, 1);
//					}
//					else if (changeInCharge === -2) {
//						addHydrogens(source, 1);
//						addHydrogens(source, 1);
//						addHydrogens(target, 1);
//						addHydrogens(target, 1);
//					}
//					source.bonds += changeInCharge;
//					target.bonds += changeInCharge;
//
//					// Remove old bond, create new one and add it to links list
//					// Simple change of bond value is buggy
//					links.splice(i, 1);
//					var newBond = {
//		 				source: bondData.source,
//		 				target: bondData.target,
//		 				bondType: newBondType,
//		 				id: generateRandomID()
//		 			};
//		 			links.push(newBond);
//
//		 			// Clear previous bond selection
//		 			bondSelected.style("filter", "");
//		 			bondSelected = null;
//
//		 			break;
//				}
//			}
//			buildMolecule();
//	  };
//
//	  window.addAtom = function (atomType) {
//	  	if (!atomType) {
//	  		Messenger().post({
//				  message: 'Internal error :(',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//	  	}
//	  	else if (!atomSelected) {
//				Messenger().post({
//				  message: 'No Atom Selected',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//			}
//			else if (!canHaveNewBond(getAtomData(atomSelected))) {
//				Messenger().post({
//				  message: 'Atom Can\'t Take Anymore Bonds',
//				  type: 'error',
//				  showCloseButton: true
//				});
//			}
//			else
//	  		addNewAtom(atomType, atomDB[atomType].size);
//	  };
//
//	 	function canHaveNewBond (atom) {
//	 		return atom.bonds < atomDB[atom.symbol].lonePairs;
//	 	}
//
//	 	function getAtomData (d3Atom) {
//	 		return d3Atom[0][0].parentNode.__data__;
//	 	}
//
//	 	function addHydrogens (atom, numHydrogens) {
//	 		var newHydrogen = function () {
//	 			return {
//		 			symbol: 'H',
//		 			size: '1',
//		 			bonds: 1,
//		 			id: generateRandomID (),
//		 			x: atom.x + getRandomInt (-15, 15),
//		 			y: atom.y + getRandomInt (-15, 15)
//		 		};
//	 		};
//	 		var tempHydrogen;
//	 		for (var i = 0; i < numHydrogens; i++) {
//	 			tempHydrogen = newHydrogen();
//	 			nodes.push(tempHydrogen);
//	 			links.push({
//	 				source: atom,
//	 				target: tempHydrogen,
//	 				bondType: 1,
//	 				id: generateRandomID()
//	 			});
//	 		}
//	 	}
//
//	 	function removeHydrogen (oldAtom) {
//	 		var target, source, bondsArr = getBonds(oldAtom.id);
//	 		for (var i = bondsArr.length - 1; i >= 0; i--) {
//	 			target = bondsArr[i].target, source = bondsArr[i].source;
//				if (target.symbol === 'H' || source.symbol === 'H' ) {
//					var hydroId = source.symbol === 'H'?
//																		source.id:
//																		target.id;
//					removeAtom(hydroId);
//					return;
//				}
//	 		}
//	 	}
//
//	 	function removeAtom (id) {
//	 		var atomToRemove = retriveAtom(id);
//	 		var bondsArr = getBonds(id);
//	 		var atomsArr = [atomToRemove.id];
//
//	 		for (var i = bondsArr.length - 1; i >= 0; i--) {
//	 			// Add atom that is a hydrogen
//	 			if (bondsArr[i].source.symbol === 'H')
//	 				atomsArr.push(bondsArr[i].source.id);
//	 			else if (bondsArr[i].target.symbol === 'H')
//	 				atomsArr.push(bondsArr[i].target.id);
//	 			else {
//	 					// Give non-hydrogen bonded atom it's lone pairs back
//						var nonHydrogenAtom = bondsArr[i].target.id !== id ?
//																									 	'target':
//																										'source';
//
//						bondsArr[i][nonHydrogenAtom].bonds -= bondsArr[i].bondType;
//		 				addHydrogens(bondsArr[i][nonHydrogenAtom], bondsArr[i].bondType);
//	 			}
//	 			// Convert atom obj to id for later processing
//	 			bondsArr[i] = bondsArr[i].id;
//	 		}
//
//	 		var spliceOut = function (arr, removeArr) {
//		 		for (var i = arr.length - 1; i >= 0; i--) {
//		 				if (removeArr.indexOf(arr[i].id) !== -1) {
//		 					arr.splice(i, 1);
//		 				}
//		 		}
//		 		return arr;
//		 	};
//
//	 		// Remove atoms marked
//	 		nodes = spliceOut (nodes, atomsArr);
//
//	 		// Remove bonds marked
//	 		links = spliceOut (links, bondsArr);
//
//	 	};
//
//	 	var retriveAtom = function  (atomID) {
//	 		for (var i = nodes.length - 1; i >= 0; i--) {
//	 			if (nodes[i].id === atomID)
//	 				return nodes[i];
//	 		}
//	 		return null;
//	 	};
//
//	  function addNewAtom (atomType, atomSize) {
//			var newAtom = {
//						symbol: atomType,
//						size: atomSize,
//						x: getAtomData(atomSelected).x + getRandomInt (-15, 15),
//						y: getAtomData(atomSelected).y + getRandomInt (-15, 15),
//						id: generateRandomID (), // Need to make sure is unique
//						bonds: 1
//					},
//		  		n = nodes.push(newAtom);
//
//		  getAtomData(atomSelected).bonds++; // Increment bond count on selected atom
//		 	addHydrogens(newAtom, atomDB[atomType].lonePairs - 1); // Adds hydrogens to new atom
//		 	removeHydrogen(getAtomData(atomSelected)); // Remove hydrogen from selected atom
//
//		  links.push({
//		  	source: newAtom,
//		  	target: getAtomData(atomSelected),
//		  	bondType: 1,
//		  	id: generateRandomID()
//		  }); // Need to make sure is unique
//
//	  	buildMolecule();
//	  }
//
//	  var getBonds = function (atomID) {
//	  	var arr = [];
//	  	for (var i = links.length - 1; i >= 0; i--) {
//	  		if (links[i].source.id === atomID || links[i].target.id === atomID)
//	  			arr.push(links[i]);
//	  	}
//	  	return arr;
//	  }
//
//	  window.deleteAtom = function () {
//	  	var oneNonHydrogenBond = function (atom) {
//	  		var atomBonds = getBonds(atom.id);
//	  		var counter = 0;
//	  		for (var i = atomBonds.length - 1; i >= 0; i--) {
//	  			if (atomBonds[i].source.symbol !== 'H' && atomBonds[i].target.symbol !== 'H')
//	  				counter++;
//	  		}
//	  		return counter === 1;
//	  	};
//
//	  	if (!atomSelected) {
//				Messenger().post({
//				  message: 'No Atom Selected',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//			}
//			else if (!oneNonHydrogenBond(getAtomData(atomSelected))) {
//				Messenger().post({
//				  message: 'Atom Must have only one non-hydrogen bond to be removed',
//				  type: 'error',
//				  showCloseButton: true
//				});
//				return;
//			}
//
//			removeAtom(getAtomData(atomSelected).id);
//			atomSelected = null;
//			buildMolecule ();
//	  };
//
//	  function tick() {
//	  	//Update old and new elements
//	    link.selectAll("line")
//	        .attr("x1", function(d) { return d.source.x; })
//	        .attr("y1", function(d) { return d.source.y; })
//	        .attr("x2", function(d) { return d.target.x; })
//	        .attr("y2", function(d) { return d.target.y; });
//
//	    node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")"; });
//	  }
//	};
//})();