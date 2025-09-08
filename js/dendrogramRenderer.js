export function renderDendrogram(jaccardSimilarity, userIds) {
    // Limpiar contenedor
    const dendrogramDiv = document.getElementById('dendrogram');
    dendrogramDiv.innerHTML = '';
    
    // Convertir similitud a distancia
    const distanceMatrix = jaccardSimilarity.map(row => 
        row.map(sim => 1 - sim)
    );
    
    // Configurar SVG
    const width = dendrogramDiv.clientWidth;
    const height = 500;
    const svg = d3.select('#dendrogram')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Configurar layout del dendrograma
    const cluster = d3.cluster()
        .size([height, width - 150]);
    
    // Construir jerarquía
    const root = buildHierarchy(distanceMatrix, userIds);
    cluster(root);
    
    // Dibujar enlaces
    svg.selectAll('.link')
        .data(root.descendants().slice(1))
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', d => {
            return `M${d.y},${d.x}C${d.parent.y + 50},${d.x} ${d.parent.y + 50},${d.parent.x} ${d.parent.y},${d.parent.x}`;
        })
        .style('fill', 'none')
        .style('stroke', '#ccc')
        .style('stroke-width', '1.5px');
    
    // Dibujar nodos
    const node = svg.selectAll('.node')
        .data(root.descendants())
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.y},${d.x})`);
    
    node.append('circle')
        .attr('r', 4.5)
        .style('fill', '#999');
    
    // Añadir etiquetas para nodos hoja
    node.filter(d => !d.children).append('text')
        .attr('dy', '0.31em')
        .attr('x', d => d.data.name ? 7 : -7)
        .attr('text-anchor', d => d.data.name ? 'start' : 'end')
        .text(d => d.data.name)
        .style('font-size', '10px')
        .style('font-family', 'sans-serif');
}

// Función auxiliar para construir jerarquía (simplificada)
function buildHierarchy(matrix, labels) {
    // Esta es una implementación simplificada para propósitos de demostración
    // En una aplicación real, se usaría un algoritmo como UPGMA o Ward
    
    // Para este ejemplo, creamos una estructura jerárquica básica
    const root = { name: "Root", children: [] };
    
    // Añadir cada usuario como hoja
    labels.forEach((label, i) => {
        root.children.push({
            name: label,
            value: 100 // Valor arbitrario para la demostración
        });
    });
    
    // Convertir a formato d3.hierarchy
    return d3.hierarchy(root);
}