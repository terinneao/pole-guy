/**
 * SVG 2D Schematic Visualizer for Pole Guy Wire System.
 * Visualizes:
 * - Pole body and underground embedment
 * - 3 Conductor levels on the Right
 * - Up to 7 Guy Wire levels on the Left leading to ground anchor
 * - Force vectors, dimension markers, and color-coded stress levels
 */

window.PoleGuyVisualizer = {
    render: function (svgContainerId, results, state) {
        const container = document.getElementById(svgContainerId);
        if (!container) return;

        const width = 900;
        const height = 650;
        const margin = { top: 40, right: 160, bottom: 60, left: 160 };

        const poleHeight = results.pole.height_m || 14.3;
        const embedment = results.pole.embedment_m || 2.0;
        const aboveGround = results.pole.above_ground_m || (poleHeight - embedment);
        const anchorDist = results.anchor.global_distance_m || 8.0;

        // Coordinate scaling
        const groundY = height - margin.bottom;
        const maxH = Math.max(aboveGround, 15.0) * 1.05;
        const availableHeight = groundY - margin.top;
        const scaleY = availableHeight / maxH; // pixels per meter

        // Center pole X
        const poleX = 450;
        const poleEmbedY = groundY + embedment * scaleY * 0.7; // scaled down embedment visually
        const poleTopY = groundY - aboveGround * scaleY;

        // Anchor position
        // Max anchor distance representation
        const maxHorizDist = Math.max(anchorDist, 10.0);
        const availableLeftWidth = poleX - margin.left;
        const scaleX = Math.min(scaleY, availableLeftWidth / (maxHorizDist * 1.15));

        const anchorX = poleX - (anchorDist * scaleX);

        let svgHtml = `
            <svg viewBox="0 0 ${width} ${height}" class="w-full h-full select-none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <!-- Marker for force arrows -->
                    <marker id="arrow-cond" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#3b82f6" />
                    </marker>
                    <marker id="arrow-anchor" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" />
                    </marker>
                    <marker id="arrow-thrust" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#8b5cf6" />
                    </marker>

                    <!-- Patterns -->
                    <pattern id="soilPattern" width="20" height="20" patternUnits="userSpaceOnUse">
                        <line x1="0" y1="20" x2="20" y2="0" stroke="#cbd5e1" stroke-width="1.2" />
                        <circle cx="6" cy="14" r="1.2" fill="#94a3b8" />
                        <circle cx="16" cy="6" r="1.2" fill="#94a3b8" />
                    </pattern>
                </defs>

                <!-- Background Subtle Grid -->
                <rect x="0" y="0" width="${width}" height="${height}" fill="#f8fafc" />

                <!-- Ground & Underground Soil -->
                <rect x="0" y="${groundY}" width="${width}" height="${height - groundY}" fill="url(#soilPattern)" opacity="0.6" />
                <line x1="0" y1="${groundY}" x2="${width}" y2="${groundY}" stroke="#334155" stroke-width="2.5" />
                <text x="30" y="${groundY - 10}" fill="#64748b" font-size="12" font-weight="600">GROUND LEVEL (0.0 m)</text>

                <!-- Anchor Lead Dimension Line -->
                <line x1="${anchorX}" y1="${groundY + 28}" x2="${poleX}" y2="${groundY + 28}" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,3" />
                <line x1="${anchorX}" y1="${groundY + 20}" x2="${anchorX}" y2="${groundY + 36}" stroke="#64748b" stroke-width="1.5" />
                <line x1="${poleX}" y1="${groundY + 20}" x2="${poleX}" y2="${groundY + 36}" stroke="#64748b" stroke-width="1.5" />
                <text x="${(anchorX + poleX) / 2}" y="${groundY + 45}" fill="#334155" font-size="12" font-weight="700" text-anchor="middle">
                    Anchor Lead L = ${anchorDist.toFixed(1)} m
                </text>

                <!-- Pole Structure -->
                <!-- Underground embedment -->
                <rect x="${poleX - 12}" y="${groundY}" width="24" height="${poleEmbedY - groundY}" fill="#94a3b8" stroke="#475569" stroke-width="2" stroke-dasharray="5,3" rx="2" />
                <!-- Concrete Pole Body -->
                <path d="M ${poleX - 10} ${groundY} L ${poleX - 7} ${poleTopY} L ${poleX + 7} ${poleTopY} L ${poleX + 10} ${groundY} Z" 
                      fill="linear-gradient(#e2e8f0, #94a3b8)" fill="#cbd5e1" stroke="#334155" stroke-width="2.2" />
                <circle cx="${poleX}" cy="${poleTopY}" r="4" fill="#475569" />

                <!-- Pole Centerline -->
                <line x1="${poleX}" y1="${poleTopY - 15}" x2="${poleX}" y2="${poleEmbedY}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="8,4" />

                <!-- Pole Height Label -->
                <text x="${poleX}" y="${poleTopY - 20}" fill="#0f172a" font-size="13" font-weight="bold" text-anchor="middle">
                    POLE TOP (${aboveGround.toFixed(1)}m / Total ${poleHeight.toFixed(1)}m)
                </text>

                <!-- Concrete Anchor Block & Eye Rod -->
                <g id="anchor-group">
                    <!-- Concrete buried block -->
                    <rect x="${anchorX - 22}" y="${groundY + 12}" width="44" height="24" fill="#64748b" stroke="#334155" stroke-width="1.5" rx="3" />
                    <!-- Anchor eye and rod -->
                    <line x1="${anchorX}" y1="${groundY}" x2="${anchorX}" y2="${groundY + 15}" stroke="#0f172a" stroke-width="4" stroke-linecap="round" />
                    <circle cx="${anchorX}" cy="${groundY}" r="6" fill="#f8fafc" stroke="#0f172a" stroke-width="3" />
                    <text x="${anchorX}" y="${groundY - 14}" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">
                        ANCHOR
                    </text>
                </g>
        `;

        // Draw Guy Wires (Up to 7 levels on the Left)
        const guys = results.guy_wires || [];
        guys.forEach((g) => {
            const h = g.height_m;
            const guyY = groundY - h * scaleY;
            const thisAnchorX = g.anchor_distance_m !== anchorDist ? (poleX - g.anchor_distance_m * scaleX) : anchorX;

            if (!g.enabled) {
                // Disabled guy wire level: light dashed line
                svgHtml += `
                    <g opacity="0.35">
                        <line x1="${thisAnchorX}" y1="${groundY}" x2="${poleX}" y2="${guyY}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,4" />
                        <circle cx="${poleX}" cy="${guyY}" r="3" fill="#cbd5e1" />
                        <text x="${poleX - 18}" y="${guyY + 4}" fill="#94a3b8" font-size="10" text-anchor="end">G${g.level} (Off)</text>
                    </g>
                `;
                return;
            }

            // Determine color based on safety factor
            let strokeColor = "#10b981"; // Safe (Green)
            let badgeBg = "#ecfdf5";
            let badgeBorder = "#10b981";
            let badgeText = "#065f46";

            if (g.status === "OVERLOADED") {
                strokeColor = "#ef4444"; // Danger (Red)
                badgeBg = "#fef2f2";
                badgeBorder = "#ef4444";
                badgeText = "#991b1b";
            } else if (g.status === "WARNING") {
                strokeColor = "#f59e0b"; // Warning (Orange)
                badgeBg = "#fffbeb";
                badgeBorder = "#f59e0b";
                badgeText = "#92400e";
            }

            const guySize = g.size_sqmm || results.guy_spec?.size_sqmm || 95;
            let guyStrokeWidth = 2.8;
            if (guySize <= 25) guyStrokeWidth = 1.6;
            else if (guySize <= 35) guyStrokeWidth = 2.0;
            else if (guySize <= 50) guyStrokeWidth = 2.4;
            else guyStrokeWidth = 3.0;

            // Guy wire attachment bolt on pole
            svgHtml += `
                <g class="guy-wire-level cursor-pointer" data-level="${g.level}">
                    <!-- Guy Wire line (${guySize} sq.mm steel strand) -->
                    <line x1="${thisAnchorX}" y1="${groundY}" x2="${poleX}" y2="${guyY}" 
                          stroke="${strokeColor}" stroke-width="${guyStrokeWidth}" stroke-linecap="round" />

                    <!-- Attachment pin -->
                    <circle cx="${poleX}" cy="${guyY}" r="4.5" fill="${strokeColor}" stroke="#ffffff" stroke-width="1.5" />

                    <!-- Guy Wire Label Badge along the line -->
                    <!-- Midpoint position -->
                    ${(() => {
                        const midX = (thisAnchorX + poleX) / 2 - (g.level - 4) * 6;
                        const midY = (groundY + guyY) / 2;
                        return `
                            <g transform="translate(${midX - 78}, ${midY - 14})">
                                <rect width="156" height="24" rx="4" fill="${badgeBg}" stroke="${badgeBorder}" stroke-width="1.2" opacity="0.95" />
                                <text x="6" y="16" fill="${badgeText}" font-size="10.5" font-weight="bold">
                                    G${g.level} (${guySize}mm²): ${Math.round(g.tension_kg)} kg (SF ${g.safety_factor})
                                </text>
                            </g>
                        `;
                    })()}

                    <!-- Left Height marker -->
                    <line x1="${poleX - 8}" y1="${guyY}" x2="${poleX - 45}" y2="${guyY}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                    <text x="${poleX - 50}" y="${guyY + 4}" fill="#475569" font-size="10.5" font-weight="600" text-anchor="end">
                        ${h.toFixed(1)}m (∠${g.angle_deg.toFixed(1)}°)
                    </text>
                </g>
            `;
        });

        // Draw Overhead Ground Wire (OHGW - installed over top conductor)
        const ohgw = results.overhead_ground_wire;
        if (ohgw) {
            const h = ohgw.height_m;
            const ohgwY = groundY - h * scaleY;
            const pullEndX = poleX + 150;

            if (!ohgw.enabled) {
                svgHtml += `
                    <g class="ohgw-level opacity-35" data-level="ohgw">
                        <line x1="${poleX}" y1="${ohgwY}" x2="${pullEndX}" y2="${ohgwY}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3" />
                        <circle cx="${poleX}" cy="${ohgwY}" r="3" fill="#94a3b8" />
                        <text x="${pullEndX + 10}" y="${ohgwY + 4}" fill="#94a3b8" font-size="10">⚡ OHGW (Disabled)</text>
                    </g>
                `;
            } else {
                const numWires = ohgw.num_conductors || 1;
                const wireStroke = Math.min(4.5, 2.2 + (numWires - 1) * 1.0);
                const badgeWidth = numWires > 1 ? 190 : 175;

                svgHtml += `
                    <g class="ohgw-level" data-level="ohgw">
                        <!-- Ground Wire Bayonet / Ridge Peak Bracket -->
                        <line x1="${poleX}" y1="${ohgwY + 8}" x2="${poleX}" y2="${ohgwY}" stroke="#334155" stroke-width="3" />
                        <circle cx="${poleX}" cy="${ohgwY}" r="4.5" fill="#0284c7" stroke="#ffffff" stroke-width="1.5" />

                        <!-- OHGW Wire pulling rightward -->
                        <line x1="${poleX + 4}" y1="${ohgwY}" x2="${pullEndX}" y2="${ohgwY}" 
                              stroke="#0284c7" stroke-width="${wireStroke}" stroke-linecap="round" />

                        <!-- OHGW Force Vector Arrow -->
                        <line x1="${pullEndX}" y1="${ohgwY}" x2="${pullEndX + 35}" y2="${ohgwY}" 
                              stroke="#0284c7" stroke-width="2.2" marker-end="url(#arrow-cond)" />

                        <!-- OHGW Info Badge -->
                        <g transform="translate(${pullEndX + 45}, ${ohgwY - 14})">
                            <rect width="${badgeWidth}" height="30" rx="4" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.2" opacity="0.95" />
                            <text x="8" y="14" fill="#0369a1" font-size="11" font-weight="bold">
                                ⚡ OHGW: ${ohgw.code} ${numWires > 1 ? `(${numWires}×)` : ''}
                            </text>
                            <text x="8" y="26" fill="#0284c7" font-size="10">
                                F = ${Math.round(ohgw.horizontal_force_kg)} kg | H = ${h.toFixed(1)}m
                            </text>
                        </g>
                    </g>
                `;
            }
        }

        // Draw Conductors (3 levels on the Right)
        const conductors = results.conductors || [];
        conductors.forEach((c) => {
            const h = c.height_m;
            const condY = groundY - h * scaleY;
            const crossarmX = poleX + 24;
            const pullEndX = poleX + 150;

            if (!c.enabled) {
                svgHtml += `
                    <g opacity="0.35">
                        <rect x="${poleX}" y="${condY - 3}" width="20" height="6" fill="#cbd5e1" />
                        <line x1="${poleX + 20}" y1="${condY}" x2="${pullEndX}" y2="${condY}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,4" />
                        <text x="${pullEndX + 10}" y="${condY + 4}" fill="#94a3b8" font-size="11">C${c.level} (Disabled)</text>
                    </g>
                `;
                return;
            }

            // Active Conductor
            const numCond = c.num_conductors || 1;
            const wireStroke = Math.min(5.5, 2.8 + (numCond - 1) * 1.2);
            const badgeWidth = numCond > 1 ? 180 : 165;

            svgHtml += `
                <g class="conductor-level" data-level="${c.level}">
                    <!-- Crossarm / Bracket -->
                    <rect x="${poleX}" y="${condY - 4}" width="26" height="8" fill="#475569" rx="1.5" />
                    <!-- Post Insulator (Bell) -->
                    <circle cx="${crossarmX + 12}" cy="${condY}" r="7" fill="#f8fafc" stroke="#3b82f6" stroke-width="2.5" />

                    <!-- Conductor Wire pulling rightward -->
                    <line x1="${crossarmX + 19}" y1="${condY}" x2="${pullEndX}" y2="${condY}" 
                          stroke="#2563eb" stroke-width="${wireStroke}" stroke-linecap="round" />

                    <!-- Conductor Tension Force Vector Arrow -->
                    <line x1="${pullEndX}" y1="${condY}" x2="${pullEndX + 35}" y2="${condY}" 
                          stroke="#3b82f6" stroke-width="2.5" marker-end="url(#arrow-cond)" />

                    <!-- Conductor Info Badge -->
                    <g transform="translate(${pullEndX + 45}, ${condY - 14})">
                        <rect width="${badgeWidth}" height="30" rx="4" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2" opacity="0.95" />
                        <text x="8" y="14" fill="#1e40af" font-size="11" font-weight="bold">
                            C${c.level}: ${c.code} ${numCond > 1 ? `(${numCond}×)` : ''}
                        </text>
                        <text x="8" y="26" fill="#1d4ed8" font-size="10">
                            F = ${Math.round(c.horizontal_force_kg)} kg | H = ${h.toFixed(1)}m
                        </text>
                    </g>
                </g>
            `;
        });

        // Draw Anchor Resultant Force Vector
        if (results.anchor.resultant_pull_kg > 0) {
            const rad = (results.anchor.resultant_angle_deg * Math.PI) / 180.0;
            const arrowLen = 50;
            // Pointing into ground/soil in direction of guy tension pull
            const vecX = anchorX - arrowLen * Math.cos(rad);
            const vecY = groundY - arrowLen * Math.sin(rad);

            svgHtml += `
                <g id="anchor-vector">
                    <line x1="${anchorX}" y1="${groundY}" x2="${vecX}" y2="${vecY}" 
                          stroke="#dc2626" stroke-width="2.5" stroke-dasharray="3,2" marker-start="url(#arrow-anchor)" />
                    <text x="${anchorX - 10}" y="${groundY + 36}" fill="#dc2626" font-size="11" font-weight="bold" text-anchor="end">
                        Resultant: ${Math.round(results.anchor.resultant_pull_kg)} kg (∠${results.anchor.resultant_angle_deg.toFixed(1)}°)
                    </text>
                </g>
            `;
        }

        // Draw Downward Compressive Thrust Vector at Pole Base
        svgHtml += `
            <g id="pole-thrust-vector">
                <line x1="${poleX}" y1="${groundY + 5}" x2="${poleX}" y2="${groundY + 45}" 
                      stroke="#8b5cf6" stroke-width="3" marker-end="url(#arrow-thrust)" />
                <text x="${poleX + 15}" y="${groundY + 32}" fill="#6d28d9" font-size="11" font-weight="bold">
                    P_thrust = ${Math.round(results.pole_base.total_downward_thrust_kg)} kg
                </text>
            </g>
        `;

        svgHtml += `</svg>`;
        container.innerHTML = svgHtml;
    }
};
