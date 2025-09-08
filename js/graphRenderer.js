export function renderGraph(userData, userIds, jaccardSimilarity, threshold) {
    // Limpiar contenedor
    const graphDiv = document.getElementById('graph');
    graphDiv.innerHTML = '';
    
    // Configurar SVG
    const width = graphDiv.clientWidth;
    const height = 500;
    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Crear tooltip
    const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);
    
    // Crear nodos y enlaces
    const nodes = userIds.map((id, i) => ({ id, index: i, titles: userData[i].titles }));
    
    const links = [];
    for (let i = 0; i < userIds.length; i++) {
        for (let j = i + 1; j < userIds.length; j++) {
            if (jaccardSimilarity[i][j] >= threshold) {
                links.push({
                    source: i,
                    target: j,
                    value: jaccardSimilarity[i][j]
                });
            }
        }
    }
    
    // Configurar fuerza de simulación
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.index).distance(d => 150 - (d.value * 100)))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Dibujar enlaces
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('class', 'link')
        .attr('stroke-width', d => d.value * 5);
    
    // Dibujar nodos
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('class', 'node')
        .attr('r', 8)
        .attr('fill', (d, i) => d3.interpolatePlasma(i / nodes.length))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Añadir etiquetas a los nodos
    const label = svg.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', '10px')
        .attr('dx', 12)
        .attr('dy', 4);
    
    // Añadir interactividad a los nodos
    node.on('mouseover', function(event, d) {
        tooltip.transition().duration(200).style('opacity', .9);
        tooltip.html(`
            <strong>Usuario:</strong> ${d.id}<br>
            <strong>Items:</strong> ${d.titles.length}<br>
            <strong>Ejemplos:</strong> ${d.titles.slice(0, 3).join(', ')}...
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
        
        // Resaltar nodos conectados
        link.style('stroke', l => {
            const isConnected = l.source.index === d.index || l.target.index === d.index;
            return isConnected ? 'steelblue' : '#999';
        })
        .style('stroke-width', l => {
            const isConnected = l.source.index === d.index || l.target.index === d.index;
            return isConnected ? l.value * 5 + 1 : l.value * 5;
        });
    })
    .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
        
        // Restaurar apariencia normal
        link.style('stroke', '#999')
            .style('stroke-width', d => d.value * 5);
    });
    
    // Actualizar posición en cada tick de la simulación
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Funciones de arrastre
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    // Añadir leyenda
    const legend = graphDiv.appendChild(document.createElement('div'));
    legend.className = 'legend';
    legend.innerHTML = `
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${d3.interpolatePlasma(0)}"></div>
            <span>Usuarios con pocos items</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${d3.interpolatePlasma(0.5)}"></div>
            <span>Usuarios con items promedio</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${d3.interpolatePlasma(1)}"></div>
            <span>Usuarios con muchos items</span>
        </div>
    `;
}