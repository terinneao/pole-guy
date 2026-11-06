/**
 * Main Application Controller for Pole Guy Wire Calculator.
 */

document.addEventListener("DOMContentLoaded", async function () {
    // Application State (Default: 22m Pole System)
    let appState = {
        pole: {
            height_m: 22.0,
            embedment_m: 2.0,
            weight_kg: 5800.0
        },
        anchor: {
            distance_m: 12.0
        },
        guy_wire_spec: {
            size_sqmm: 95.0,
            name: "95 sq.mm Galvanized Steel Strand",
            rts_kg: 8528.0, // High Strength default
            unit_weight_kg_m: 0.764,
            required_sf: 2.0
        },
        calculation_method: "elastic",
        overhead_ground_wire: {
            enabled: true,
            code: "GSW-35",
            name: "35 sq.mm Galvanized Steel Strand",
            height_m: 21.8,
            span_m: 40.0,
            sag_m: 0.10,
            num_conductors: 1,
            weight_kg_per_m: 0.272,
            breaking_strength_kg: 2330.0,
            overall_diameter_mm: 7.5,
            tension_mode: "sag_span",
            wind_pressure_kg_m2: 40.0,
            deviation_angle_deg: 0.0
        },
        conductors: [
            {
                level: 1,
                enabled: true,
                height_m: 18.75,
                code: "AAC-400",
                name: "AAC 400 sq.mm",
                breaking_strength_kg: 6680.0,
                weight_kg_per_m: 1.100,
                overall_diameter_mm: 26.0,
                tension_mode: "sag_span",
                span_m: 40.0,
                sag_m: 0.14,
                num_conductors: 2,
                wind_pressure_kg_m2: 40.0,
                deviation_angle_deg: 0.0
            },
            {
                level: 2,
                enabled: true,
                height_m: 16.05,
                code: "AAC-400",
                name: "AAC 400 sq.mm",
                breaking_strength_kg: 6680.0,
                weight_kg_per_m: 1.100,
                overall_diameter_mm: 26.0,
                tension_mode: "sag_span",
                span_m: 40.0,
                sag_m: 0.14,
                num_conductors: 2,
                wind_pressure_kg_m2: 40.0,
                deviation_angle_deg: 0.0
            },
            {
                level: 3,
                enabled: true,
                height_m: 13.35,
                code: "AAC-400",
                name: "AAC 400 sq.mm",
                breaking_strength_kg: 6680.0,
                weight_kg_per_m: 1.100,
                overall_diameter_mm: 26.0,
                tension_mode: "sag_span",
                span_m: 40.0,
                sag_m: 0.14,
                num_conductors: 2,
                wind_pressure_kg_m2: 40.0,
                deviation_angle_deg: 0.0
            }
        ],
        guy_wires: [
            { level: 1, enabled: true, height_m: 19.75, anchor_distance_m: 12.0, size_sqmm: 50.0 },
            { level: 2, enabled: true, height_m: 19.25, anchor_distance_m: 12.0, size_sqmm: 95.0 },
            { level: 3, enabled: true, height_m: 18.25, anchor_distance_m: 12.0, size_sqmm: 95.0 },
            { level: 4, enabled: true, height_m: 16.75, anchor_distance_m: 12.0, size_sqmm: 95.0 },
            { level: 5, enabled: true, height_m: 15.55, anchor_distance_m: 12.0, size_sqmm: 95.0 },
            { level: 6, enabled: true, height_m: 13.65, anchor_distance_m: 12.0, size_sqmm: 95.0 },
            { level: 7, enabled: true, height_m: 12.75, anchor_distance_m: 12.0, size_sqmm: 95.0 }
        ]
    };

    let cachedConductors = [];

    // Initialize conductors from SQL API
    async function initConductors() {
        cachedConductors = await ConductorDB.fetchConductors();
        populateConductorSelects();
    }

    // Helper to generate conductor select options from cached SQL conductors
    function buildConductorSelectOptionsHtml(selectedCode) {
        if (!cachedConductors || cachedConductors.length === 0) {
            return `<option value="${selectedCode}" selected>${selectedCode}</option>`;
        }
        const groups = {};
        cachedConductors.forEach(c => {
            if (!groups[c.conductor_type]) groups[c.conductor_type] = [];
            groups[c.conductor_type].push(c);
        });

        let html = "";
        for (const [type, list] of Object.entries(groups)) {
            html += `<optgroup label="${type} Conductors">`;
            list.forEach(c => {
                const isSel = (c.code === selectedCode) ? "selected" : "";
                html += `<option value="${c.code}" data-conductor='${JSON.stringify(c)}' ${isSel}>${c.code} (${c.name}) - RTS: ${c.breaking_strength_kg} kg</option>`;
            });
            html += `</optgroup>`;
        }
        return html;
    }

    // Populate all conductor select dropdowns from SQL DB
    function populateConductorSelects() {
        const groups = {};
        cachedConductors.forEach(c => {
            if (!groups[c.conductor_type]) groups[c.conductor_type] = [];
            groups[c.conductor_type].push(c);
        });

        appState.conductors.forEach((c) => {
            const select = document.getElementById(`cond-select-${c.level}`);
            if (!select) return;

            const currentVal = c.code;
            select.innerHTML = "";

            for (const [type, list] of Object.entries(groups)) {
                const optGroup = document.createElement("optgroup");
                optGroup.label = `${type} Conductors`;
                list.forEach(item => {
                    const opt = document.createElement("option");
                    opt.value = item.code;
                    opt.textContent = `${item.code} (${item.name}) - RTS: ${item.breaking_strength_kg} kg`;
                    opt.dataset.conductor = JSON.stringify(item);
                    if (item.code === currentVal) {
                        opt.selected = true;
                    }
                    optGroup.appendChild(opt);
                });
                select.appendChild(optGroup);
            }
        });
    }

    // Recalculate and update the entire UI
    function runCalculation() {
        // Run calculation engine
        const results = PoleGuyCalculator.calculate(appState);

        // Update SVG Visualizer
        PoleGuyVisualizer.render("visualizer-container", results, appState);

        // Update KPI Summary Cards
        updateSummaryKPIs(results);

        // Update Guy Wire Results Table
        updateGuyWireTable(results);

        // Update Conductor Moment Preview
        updateConductorMomentPreviews(results);

        // Update Anchor & Pole Base Details
        updateReactionsUI(results);
    }

    function updateSummaryKPIs(results) {
        // Total Overturning Moment
        const otEl = document.getElementById("kpi-overturning-moment");
        if (otEl) otEl.textContent = `${Math.round(results.summary.total_overturning_moment_kg_m).toLocaleString()} kg·m`;

        const otSublabel = document.getElementById("kpi-overturning-sublabel");
        if (otSublabel) {
            const activeCond = (results.conductors || []).filter(c => c.enabled).length;
            const totalCond = (results.conductors || []).length;
            const ohgwText = (results.overhead_ground_wire && results.overhead_ground_wire.enabled) ? " + OHGW" : "";
            otSublabel.textContent = `From ${activeCond}/${totalCond} Conductors${ohgwText}`;
        }

        // Total Guy Resisting Moment
        const rmEl = document.getElementById("kpi-resisting-moment");
        if (rmEl) rmEl.textContent = `${Math.round(results.summary.total_resisting_moment_kg_m).toLocaleString()} kg·m`;

        // Total Anchor Pull Resultant
        const apEl = document.getElementById("kpi-anchor-pull");
        if (apEl) apEl.textContent = `${Math.round(results.anchor.resultant_pull_kg).toLocaleString()} kg`;

        // Downward Pole Thrust
        const ptEl = document.getElementById("kpi-pole-thrust");
        if (ptEl) ptEl.textContent = `${Math.round(results.pole_base.total_downward_thrust_kg).toLocaleString()} kg`;

        // Guy Wires Count Label
        const guysCountLabel = document.getElementById("kpi-guys-count-label");
        if (guysCountLabel) {
            const activeGuys = (results.guy_wires || []).filter(g => g.enabled).length;
            const totalGuys = (results.guy_wires || []).length;
            guysCountLabel.textContent = `From ${activeGuys} Active (${totalGuys} Guy Wires)`;
        }

        // Overall Status Badge
        const statusBadge = document.getElementById("kpi-status-badge");
        if (statusBadge) {
            statusBadge.className = "px-3 py-1 text-xs font-bold rounded-full uppercase ";
            if (results.status === "SAFE") {
                statusBadge.textContent = "SAFE (STABLE)";
                statusBadge.className += "bg-emerald-100 text-emerald-800 border border-emerald-300";
            } else if (results.status === "WARNING") {
                statusBadge.textContent = "WARNING (SF < 2.0)";
                statusBadge.className += "bg-amber-100 text-amber-800 border border-amber-300";
            } else {
                statusBadge.textContent = "OVERLOADED (DANGER)";
                statusBadge.className += "bg-red-100 text-red-800 border border-red-300 animate-pulse";
            }
        }
    }

    function updateGuyWireTable(results) {
        const tbody = document.getElementById("guy-table-body");
        const tableLabel = document.getElementById("table-guy-spec-label");
        if (tableLabel && results.guy_spec) {
            const activeGuys = results.guy_wires.filter(g => g.enabled);
            const hasMultipleSizes = activeGuys.length > 1 && activeGuys.some(g => g.size_sqmm !== activeGuys[0].size_sqmm);
            tableLabel.textContent = hasMultipleSizes
                ? "Mixed Multi-Size Strands"
                : (results.guy_spec.name || `${results.guy_spec.size_sqmm} sq.mm Galvanized Steel Strand`);
        }
        if (!tbody) return;

        let html = "";
        results.guy_wires.forEach(g => {
            const sizeLabel = g.size_sqmm ? `${g.size_sqmm} mm²` : "95 mm²";
            if (!g.enabled) {
                html += `
                    <tr class="opacity-40 bg-slate-50 text-slate-400">
                        <td class="py-2 px-3 font-semibold text-center">
                            <span>G${g.level}</span>
                            <span class="block text-[10px] text-slate-400 font-normal">${sizeLabel}</span>
                        </td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center">-</td>
                        <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-slate-200 text-slate-600">OFF</span></td>
                    </tr>
                `;
                return;
            }

            let badgeClass = "bg-emerald-100 text-emerald-800 border border-emerald-300";
            if (g.status === "OVERLOADED") badgeClass = "bg-rose-100 text-rose-800 border border-rose-300 font-bold";
            else if (g.status === "WARNING") badgeClass = "bg-amber-100 text-amber-800 border border-amber-300 font-medium";

            html += `
                <tr class="hover:bg-slate-50 transition border-b border-slate-100">
                    <td class="py-2 px-3 font-bold text-slate-800 text-center">
                        <span>G${g.level}</span>
                        <span class="block text-[10px] text-emerald-700 font-semibold">${sizeLabel}</span>
                    </td>
                    <td class="py-2.5 px-3 text-right font-medium">${g.height_m.toFixed(1)} m</td>
                    <td class="py-2.5 px-3 text-right text-slate-600">${g.slope_length_m.toFixed(1)} m (${g.angle_deg.toFixed(1)}°)</td>
                    <td class="py-2.5 px-3 text-right font-bold text-slate-900">${Math.round(g.tension_kg).toLocaleString()} kg</td>
                    <td class="py-2.5 px-3 text-right text-slate-700">${Math.round(g.horizontal_force_kg).toLocaleString()} kg</td>
                    <td class="py-2.5 px-3 text-right text-slate-700">${Math.round(g.vertical_force_kg).toLocaleString()} kg</td>
                    <td class="py-2.5 px-3 text-right font-bold ${g.safety_factor < 2.0 ? 'text-amber-600' : 'text-emerald-700'}">${g.safety_factor.toFixed(2)}</td>
                    <td class="py-2.5 px-3 text-center">
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${badgeClass}">${g.status}</span>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    function updateConductorMomentPreviews(results) {
        results.conductors.forEach(c => {
            const previewEl = document.getElementById(`cond-moment-${c.level}`);
            const tensionBadge = document.getElementById(`cond-tension-badge-${c.level}`);

            if (tensionBadge) {
                if (c.enabled) {
                    const numCond = c.num_conductors || 1;
                    const windInfo = (c.wind_pressure_kg_m2 > 0 && c.resultant_weight_kg_m)
                        ? ` [wr: ${c.resultant_weight_kg_m.toFixed(2)} kg/m]`
                        : "";
                    const tensionText = numCond > 1
                        ? `T: ${Math.round(c.single_tension_kg)} kg × ${numCond}${windInfo} (${c.tension_pct_rts || 0}% RTS)`
                        : `T: ${Math.round(c.single_tension_kg)} kg${windInfo} (${c.tension_pct_rts || 0}% RTS)`;
                    tensionBadge.textContent = tensionText;
                    tensionBadge.className = "font-semibold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded text-[11px]";
                } else {
                    tensionBadge.textContent = "Disabled";
                    tensionBadge.className = "font-medium text-slate-400 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[11px]";
                }
            }

            if (previewEl) {
                if (c.enabled) {
                    previewEl.textContent = `F: ${Math.round(c.horizontal_force_kg)} kg | M: ${Math.round(c.moment_kg_m).toLocaleString()} kg·m`;
                    previewEl.className = "font-semibold text-blue-800 bg-blue-100 border border-blue-300 px-2 py-0.5 rounded text-[11px]";
                } else {
                    previewEl.textContent = "Off";
                    previewEl.className = "font-medium text-slate-400 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[11px]";
                }
            }
        });

        // Update OHGW Badges
        const ohgw = results.overhead_ground_wire;
        const ohgwTensionBadge = document.getElementById("ohgw-tension-badge");
        const ohgwMomentBadge = document.getElementById("ohgw-moment-badge");
        if (ohgw && ohgwTensionBadge && ohgwMomentBadge) {
            if (ohgw.enabled) {
                const numWires = ohgw.num_conductors || 1;
                const windInfo = (ohgw.wind_pressure_kg_m2 > 0 && ohgw.resultant_weight_kg_m)
                    ? ` [wr: ${ohgw.resultant_weight_kg_m.toFixed(2)} kg/m]`
                    : "";
                const tensionText = numWires > 1
                    ? `T: ${Math.round(ohgw.single_tension_kg)} kg × ${numWires}${windInfo} (${ohgw.tension_pct_rts || 0}% RTS)`
                    : `T: ${Math.round(ohgw.single_tension_kg)} kg${windInfo} (${ohgw.tension_pct_rts || 0}% RTS)`;
                ohgwTensionBadge.textContent = tensionText;
                ohgwTensionBadge.className = "font-semibold text-sky-900 bg-sky-100 border border-sky-300 px-2 py-0.5 rounded text-[11px]";

                ohgwMomentBadge.textContent = `F: ${Math.round(ohgw.horizontal_force_kg)} kg | M: ${Math.round(ohgw.moment_kg_m).toLocaleString()} kg·m`;
                ohgwMomentBadge.className = "font-semibold text-blue-800 bg-blue-100 border border-blue-300 px-2 py-0.5 rounded text-[11px]";
            } else {
                ohgwTensionBadge.textContent = "Disabled";
                ohgwTensionBadge.className = "font-medium text-slate-400 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[11px]";
                ohgwMomentBadge.textContent = "Off";
                ohgwMomentBadge.className = "font-medium text-slate-400 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[11px]";
            }
        }
    }

    function updateReactionsUI(results) {
        const ancH = document.getElementById("anchor-h-pull");
        if (ancH) ancH.textContent = `${Math.round(results.anchor.total_horizontal_pull_kg).toLocaleString()} kg`;

        const ancV = document.getElementById("anchor-v-uplift");
        if (ancV) ancV.textContent = `${Math.round(results.anchor.total_vertical_uplift_kg).toLocaleString()} kg`;

        const ancAngle = document.getElementById("anchor-angle");
        if (ancAngle) ancAngle.textContent = `${results.anchor.resultant_angle_deg.toFixed(1)}°`;

        const shearEl = document.getElementById("pole-base-shear");
        if (shearEl) shearEl.textContent = `${Math.round(results.pole_base.net_horizontal_shear_kg).toLocaleString()} kg`;

        const balancePct = document.getElementById("moment-balance-pct");
        if (balancePct) balancePct.textContent = `${results.pole_base.moment_balance_pct.toFixed(1)}%`;
    }

    // Standard Guy Wire Specs Dictionary
    const GUY_WIRE_SPECS_DATA = {
        95: {
            size_sqmm: 95.0,
            name: "95 sq.mm Galvanized Steel Strand",
            area_label: "95 sq.mm (7/4.15 mm)",
            badge_label: "95 sq.mm",
            unit_weight_kg_m: 0.764,
            rts_options: [
                { value: 8528, label: "High Strength (8,528 kg / 83.6 kN)", default: true },
                { value: 11600, label: "Extra High Strength (11,600 kg / 113.8 kN)" },
                { value: "custom", label: "Custom RTS (kg)..." }
            ]
        },
        50: {
            size_sqmm: 50.0,
            name: "50 sq.mm Galvanized Steel Strand",
            area_label: "50 sq.mm (7/3.00 mm)",
            badge_label: "50 sq.mm",
            unit_weight_kg_m: 0.392,
            rts_options: [
                { value: 3355, label: "Standard / Utility (3,355 kg / 32.9 kN)", default: true },
                { value: 4898, label: "High Strength (4,898 kg / 48.0 kN)" },
                { value: 6985, label: "Extra High Strength (6,985 kg / 68.5 kN)" },
                { value: "custom", label: "Custom RTS (kg)..." }
            ]
        },
        35: {
            size_sqmm: 35.0,
            name: "35 sq.mm Galvanized Steel Strand",
            area_label: "35 sq.mm (7/2.50 mm)",
            badge_label: "35 sq.mm",
            unit_weight_kg_m: 0.272,
            rts_options: [
                { value: 2330, label: "Standard / Utility (2,330 kg / 22.85 kN)", default: true },
                { value: "custom", label: "Custom RTS (kg)..." }
            ]
        },
        25: {
            size_sqmm: 25.0,
            name: "25 sq.mm Galvanized Steel Strand",
            area_label: "25 sq.mm (7/2.10 mm)",
            badge_label: "25 sq.mm",
            unit_weight_kg_m: 0.192,
            rts_options: [
                { value: 1647, label: "Standard / Utility (1,647 kg / 16.15 kN)", default: true },
                { value: "custom", label: "Custom RTS (kg)..." }
            ]
        }
    };

    let setGuySizeUI = null;
    let renderGuyWireInputs = null;
    let renderConductorInputs = null;

    // Attach Event Handlers for Guy Wires inputs
    function setupGuyWireInputs() {
        // Global Anchor Distance
        const globalAnchorInput = document.getElementById("global-anchor-dist");
        if (globalAnchorInput) {
            globalAnchorInput.value = appState.anchor.distance_m;
            globalAnchorInput.addEventListener("input", (e) => {
                const val = parseFloat(e.target.value) || 1.0;
                appState.anchor.distance_m = val;
                // update each guy level anchor dist if matching
                appState.guy_wires.forEach(g => { g.anchor_distance_m = val; });
                runCalculation();
            });
        }

        // Guy Wire Size & Specification Selector
        const guySizeSelect = document.getElementById("guy-size-select");
        const guyBadgeSize = document.getElementById("guy-badge-size");
        const guyAreaDisplay = document.getElementById("guy-area-display");
        const guyWeightDisplay = document.getElementById("guy-weight-display");
        const guyTableSpecLabel = document.getElementById("table-guy-spec-label");
        const guyRtsSelect = document.getElementById("guy-rts-preset");
        const customRtsInput = document.getElementById("guy-rts-custom");

        function populateGuyRtsOptions(size, selectedRts = null) {
            const spec = GUY_WIRE_SPECS_DATA[size] || GUY_WIRE_SPECS_DATA[95];
            if (!guyRtsSelect) return;

            guyRtsSelect.innerHTML = "";
            let matched = false;
            let defaultVal = spec.rts_options[0].value;

            spec.rts_options.forEach(opt => {
                const optEl = document.createElement("option");
                optEl.value = opt.value;
                optEl.textContent = opt.label;
                if (selectedRts && opt.value !== "custom" && Math.abs(parseFloat(opt.value) - selectedRts) < 1.0) {
                    optEl.selected = true;
                    matched = true;
                } else if (!selectedRts && opt.default) {
                    optEl.selected = true;
                    defaultVal = opt.value;
                    matched = true;
                }
                guyRtsSelect.appendChild(optEl);
            });

            if (!matched && selectedRts) {
                guyRtsSelect.value = "custom";
                if (customRtsInput) {
                    customRtsInput.classList.remove("hidden");
                    customRtsInput.value = selectedRts;
                }
            } else {
                if (customRtsInput) {
                    customRtsInput.classList.add("hidden");
                    customRtsInput.value = (guyRtsSelect.value !== "custom") ? guyRtsSelect.value : defaultVal;
                }
            }
        }

        setGuySizeUI = function (size, updateRts = true) {
            const spec = GUY_WIRE_SPECS_DATA[size] || GUY_WIRE_SPECS_DATA[95];
            appState.guy_wire_spec.size_sqmm = spec.size_sqmm;
            appState.guy_wire_spec.name = spec.name;
            appState.guy_wire_spec.unit_weight_kg_m = spec.unit_weight_kg_m;

            if (guySizeSelect) guySizeSelect.value = String(size);
            if (guyBadgeSize) guyBadgeSize.textContent = spec.badge_label;
            if (guyAreaDisplay) guyAreaDisplay.textContent = spec.area_label;
            if (guyWeightDisplay) guyWeightDisplay.textContent = `${spec.unit_weight_kg_m} kg/m`;
            if (guyTableSpecLabel) guyTableSpecLabel.textContent = spec.name;

            if (updateRts) {
                populateGuyRtsOptions(size);
                const selectedVal = parseFloat(guyRtsSelect.value) || spec.rts_options[0].value;
                appState.guy_wire_spec.rts_kg = selectedVal;
            }
        };

        if (guySizeSelect) {
            guySizeSelect.addEventListener("change", (e) => {
                const newSize = parseInt(e.target.value) || 95;
                setGuySizeUI(newSize, true);
                // Also synchronize all guy wire level dropdowns and appState
                appState.guy_wires.forEach(g => {
                    g.size_sqmm = newSize;
                });
                renderGuyWireInputs();
                runCalculation();
            });
        }

        // Sync All Guy Sizes Button
        const btnSyncGuySizes = document.getElementById("btn-sync-guy-sizes");
        if (btnSyncGuySizes) {
            btnSyncGuySizes.addEventListener("click", () => {
                const targetSize = appState.guy_wire_spec.size_sqmm || 95.0;
                appState.guy_wires.forEach(g => {
                    g.size_sqmm = targetSize;
                });
                renderGuyWireInputs();
                runCalculation();
            });
        }

        // Guy Wire RTS selection (Preset vs Custom)
        if (guyRtsSelect && customRtsInput) {
            guyRtsSelect.addEventListener("change", (e) => {
                const curSize = appState.guy_wire_spec.size_sqmm || 95;
                const defVal = curSize === 50 ? 3355 : (curSize === 35 ? 2330 : (curSize === 25 ? 1647 : 8528));
                if (e.target.value === "custom") {
                    customRtsInput.classList.remove("hidden");
                    appState.guy_wire_spec.rts_kg = parseFloat(customRtsInput.value) || defVal;
                } else {
                    customRtsInput.classList.add("hidden");
                    const val = parseFloat(e.target.value) || defVal;
                    appState.guy_wire_spec.rts_kg = val;
                    customRtsInput.value = val;
                }
                runCalculation();
            });

            customRtsInput.addEventListener("input", (e) => {
                const curSize = appState.guy_wire_spec.size_sqmm || 95;
                const defVal = curSize === 50 ? 3355 : (curSize === 35 ? 2330 : (curSize === 25 ? 1647 : 8528));
                appState.guy_wire_spec.rts_kg = parseFloat(e.target.value) || defVal;
                runCalculation();
            });
        }

        // Dynamic Guy Wire Rows Rendering
        renderGuyWireInputs = function () {
            const container = document.getElementById("guy-wires-inputs-container");
            if (!container) return;

            const count = appState.guy_wires.length;
            let html = "";

            appState.guy_wires.forEach((g, idx) => {
                const isTop = (idx === 0);
                const isBtm = (idx === count - 1 && count > 1);
                const labelSuffix = isTop ? " (Top)" : (isBtm ? " (Btm)" : "");
                const sizeVal = g.size_sqmm || 95;

                html += `
                    <div class="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-200 gap-1 hover:border-slate-300 transition" data-index="${idx}">
                        <div class="flex items-center gap-1.5 min-w-[72px]">
                            <input type="checkbox" id="guy-enable-${g.level}" ${g.enabled ? "checked" : ""} class="guy-row-enable w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer" data-index="${idx}">
                            <label for="guy-enable-${g.level}" class="font-bold text-slate-800 text-[11px] sm:text-xs cursor-pointer select-none">G${g.level}${labelSuffix}</label>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <select id="guy-size-${g.level}" class="guy-row-size text-[11px] rounded border-slate-300 py-1 px-1 bg-white font-semibold text-slate-700 cursor-pointer" data-index="${idx}">
                                <option value="95" ${sizeVal === 95 ? "selected" : ""}>95 mm²</option>
                                <option value="50" ${sizeVal === 50 ? "selected" : ""}>50 mm²</option>
                                <option value="35" ${sizeVal === 35 ? "selected" : ""}>35 mm²</option>
                                <option value="25" ${sizeVal === 25 ? "selected" : ""}>25 mm²</option>
                            </select>
                            <div class="flex items-center gap-1">
                                <span class="text-slate-500 text-[11px]">H:</span>
                                <input type="number" id="guy-height-${g.level}" value="${g.height_m}" step="0.1" class="guy-row-height w-14 rounded border-slate-300 py-1 px-1 text-center font-bold text-xs" data-index="${idx}">
                                <span class="text-slate-400 text-[11px]">m</span>
                            </div>
                            <button type="button" class="btn-remove-guy p-1 rounded hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition cursor-pointer" data-index="${idx}" title="Remove this guy wire" ${count <= 1 ? "disabled style='visibility: hidden;'" : ""}>
                                <i class="fa-solid fa-trash-can text-[11px]"></i>
                            </button>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;

            // Attach event listeners
            container.querySelectorAll(".guy-row-enable").forEach(chk => {
                chk.addEventListener("change", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.guy_wires[i]) {
                        appState.guy_wires[i].enabled = e.target.checked;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".guy-row-size").forEach(sel => {
                sel.addEventListener("change", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.guy_wires[i]) {
                        appState.guy_wires[i].size_sqmm = parseFloat(e.target.value) || 95.0;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".guy-row-height").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.guy_wires[i]) {
                        appState.guy_wires[i].height_m = parseFloat(e.target.value) || 0;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".btn-remove-guy").forEach(btn => {
                btn.addEventListener("click", () => {
                    const i = parseInt(btn.dataset.index);
                    removeGuyWire(i);
                });
            });
        };

        function addGuyWire() {
            const count = appState.guy_wires.length;
            let newHeight = 10.0;
            if (count > 0) {
                const lowestHeight = Math.min(...appState.guy_wires.map(g => g.height_m));
                if (lowestHeight > 3.0) {
                    newHeight = Math.max(2.0, parseFloat((lowestHeight - 1.5).toFixed(2)));
                } else {
                    newHeight = Math.max(1.5, parseFloat((lowestHeight * 0.8).toFixed(2)));
                }
            }
            const targetSize = appState.guy_wire_spec.size_sqmm || 95.0;
            const globalAnchor = appState.anchor.distance_m || 12.0;

            appState.guy_wires.push({
                level: count + 1,
                enabled: true,
                height_m: newHeight,
                anchor_distance_m: globalAnchor,
                size_sqmm: targetSize
            });

            renderGuyWireInputs();
            runCalculation();
        }

        function removeGuyWire(index) {
            if (appState.guy_wires.length <= 1) return;
            appState.guy_wires.splice(index, 1);
            appState.guy_wires.forEach((g, idx) => {
                g.level = idx + 1;
            });
            renderGuyWireInputs();
            runCalculation();
        }

        // Add Guy Wire Button
        const btnAddGuyWire = document.getElementById("btn-add-guy-wire");
        if (btnAddGuyWire) {
            btnAddGuyWire.addEventListener("click", () => {
                addGuyWire();
            });
        }

        // Initial render of guy wire inputs
        renderGuyWireInputs();

        // Calculation Method Selector
        const methodSelect = document.getElementById("calc-method-select");
        if (methodSelect) {
            methodSelect.addEventListener("change", (e) => {
                appState.calculation_method = e.target.value;
                runCalculation();
            });
        }

        // Required Safety Factor
        const reqSfInput = document.getElementById("required-sf-input");
        if (reqSfInput) {
            reqSfInput.addEventListener("input", (e) => {
                appState.guy_wire_spec.required_sf = parseFloat(e.target.value) || 2.0;
                runCalculation();
            });
        }

        // Initialize Guy Wire Spec UI
        if (setGuySizeUI) {
            setGuySizeUI(appState.guy_wire_spec.size_sqmm || 95, false);
            populateGuyRtsOptions(appState.guy_wire_spec.size_sqmm || 95, appState.guy_wire_spec.rts_kg);
        }
    }

    // Attach Event Handlers for Conductor inputs
    function setupConductorInputs() {
        // Quick Apply Span, Sag, Wind and Qty to all 3 conductors and OHGW
        const quickNumInput = document.getElementById("quick-num-all");
        const quickSpanInput = document.getElementById("quick-span-all");
        const quickSagInput = document.getElementById("quick-sag-all");
        const quickWindInput = document.getElementById("quick-wind-all");
        const btnApplyAll = document.getElementById("btn-apply-span-sag-all");

        if (btnApplyAll && quickSpanInput && quickSagInput) {
            btnApplyAll.addEventListener("click", () => {
                const numVal = Math.max(1, parseInt(quickNumInput ? quickNumInput.value : 2) || 2);
                const spanVal = parseFloat(quickSpanInput.value) || 40;
                const sagVal = parseFloat(quickSagInput.value) || 0.14;
                const windVal = Math.max(0, parseFloat(quickWindInput ? quickWindInput.value : 40) || 40);

                appState.conductors.forEach((c) => {
                    c.num_conductors = numVal;
                    c.span_m = spanVal;
                    c.sag_m = sagVal;
                    c.wind_pressure_kg_m2 = windVal;
                });
                renderConductorInputs();
                if (appState.overhead_ground_wire) {
                    appState.overhead_ground_wire.span_m = spanVal;
                    appState.overhead_ground_wire.wind_pressure_kg_m2 = windVal;
                    const ohgwSpanEl = document.getElementById("ohgw-span");
                    const ohgwWindEl = document.getElementById("ohgw-wind");
                    if (ohgwSpanEl) ohgwSpanEl.value = spanVal;
                    if (ohgwWindEl) ohgwWindEl.value = windVal;
                }
                runCalculation();
            });
        }

        // Overhead Ground Wire (OHGW) Inputs
        const ohgwChk = document.getElementById("ohgw-enable");
        const ohgwSpecSelect = document.getElementById("ohgw-spec-select");
        const ohgwNumInput = document.getElementById("ohgw-num");
        const ohgwHeightInput = document.getElementById("ohgw-height");
        const ohgwSpanInput = document.getElementById("ohgw-span");
        const ohgwSagInput = document.getElementById("ohgw-sag");
        const ohgwWindInput = document.getElementById("ohgw-wind");
        const ohgwAngleInput = document.getElementById("ohgw-angle");

        if (ohgwChk) {
            ohgwChk.checked = appState.overhead_ground_wire.enabled;
            ohgwChk.addEventListener("change", (e) => {
                appState.overhead_ground_wire.enabled = e.target.checked;
                runCalculation();
            });
        }

        if (ohgwSpecSelect) {
            ohgwSpecSelect.value = appState.overhead_ground_wire.code || "GSW-35";
            ohgwSpecSelect.addEventListener("change", (e) => {
                const val = e.target.value;
                if (val === "GSW-25") {
                    appState.overhead_ground_wire.code = "GSW-25";
                    appState.overhead_ground_wire.name = "25 sq.mm Galvanized Steel Strand";
                    appState.overhead_ground_wire.weight_kg_per_m = 0.192;
                    appState.overhead_ground_wire.breaking_strength_kg = 1647.0;
                    appState.overhead_ground_wire.overall_diameter_mm = 6.3;
                } else if (val === "GSW-35") {
                    appState.overhead_ground_wire.code = "GSW-35";
                    appState.overhead_ground_wire.name = "35 sq.mm Galvanized Steel Strand";
                    appState.overhead_ground_wire.weight_kg_per_m = 0.272;
                    appState.overhead_ground_wire.breaking_strength_kg = 2330.0;
                    appState.overhead_ground_wire.overall_diameter_mm = 7.5;
                } else if (val === "GSW-50") {
                    appState.overhead_ground_wire.code = "GSW-50";
                    appState.overhead_ground_wire.name = "50 sq.mm Galvanized Steel Strand";
                    appState.overhead_ground_wire.weight_kg_per_m = 0.392;
                    appState.overhead_ground_wire.breaking_strength_kg = 3355.0;
                    appState.overhead_ground_wire.overall_diameter_mm = 9.0;
                } else if (val === "GSW-95") {
                    appState.overhead_ground_wire.code = "GSW-95";
                    appState.overhead_ground_wire.name = "95 sq.mm Galvanized Steel Strand";
                    appState.overhead_ground_wire.weight_kg_per_m = 0.764;
                    appState.overhead_ground_wire.breaking_strength_kg = 8528.0;
                    appState.overhead_ground_wire.overall_diameter_mm = 12.5;
                } else if (val === "ACSR-50") {
                    appState.overhead_ground_wire.code = "ACSR-50";
                    appState.overhead_ground_wire.name = "ACSR 50 sq.mm";
                    appState.overhead_ground_wire.weight_kg_per_m = 0.187;
                    appState.overhead_ground_wire.breaking_strength_kg = 1480.0;
                    appState.overhead_ground_wire.overall_diameter_mm = 9.0;
                }
                runCalculation();
            });
        }

        if (ohgwNumInput) {
            ohgwNumInput.value = appState.overhead_ground_wire.num_conductors || 1;
            ohgwNumInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.num_conductors = Math.max(1, parseInt(e.target.value) || 1);
                runCalculation();
            });
        }

        if (ohgwHeightInput) {
            ohgwHeightInput.value = appState.overhead_ground_wire.height_m;
            ohgwHeightInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.height_m = parseFloat(e.target.value) || 0;
                runCalculation();
            });
        }

        if (ohgwSpanInput) {
            ohgwSpanInput.value = appState.overhead_ground_wire.span_m;
            ohgwSpanInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.span_m = parseFloat(e.target.value) || 40;
                runCalculation();
            });
        }

        if (ohgwSagInput) {
            ohgwSagInput.value = appState.overhead_ground_wire.sag_m;
            ohgwSagInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.sag_m = parseFloat(e.target.value) || 0.50;
                runCalculation();
            });
        }

        if (ohgwWindInput) {
            ohgwWindInput.value = (appState.overhead_ground_wire.wind_pressure_kg_m2 !== undefined) ? appState.overhead_ground_wire.wind_pressure_kg_m2 : 40;
            ohgwWindInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.wind_pressure_kg_m2 = Math.max(0, parseFloat(e.target.value) || 0);
                runCalculation();
            });
        }

        if (ohgwAngleInput) {
            ohgwAngleInput.value = appState.overhead_ground_wire.deviation_angle_deg || 0;
            ohgwAngleInput.addEventListener("input", (e) => {
                appState.overhead_ground_wire.deviation_angle_deg = parseFloat(e.target.value) || 0;
                runCalculation();
            });
        }

        // Dynamic Conductor Rows Rendering
        renderConductorInputs = function () {
            const container = document.getElementById("conductors-inputs-container");
            if (!container) return;

            const count = appState.conductors.length;
            let html = "";

            appState.conductors.forEach((c, idx) => {
                let labelSuffix = "";
                if (count === 1) {
                    labelSuffix = "";
                } else if (count === 2) {
                    labelSuffix = (idx === 0) ? " (Top Phase)" : " (Bottom Phase)";
                } else if (count === 3) {
                    labelSuffix = (idx === 0) ? " (Top Phase)" : ((idx === 1) ? " (Middle Phase)" : " (Bottom Phase)");
                } else {
                    labelSuffix = (idx === 0) ? " (Top Phase)" : ((idx === count - 1) ? " (Bottom Phase)" : ` (Phase ${idx + 1})`);
                }

                const windVal = (c.wind_pressure_kg_m2 !== undefined) ? c.wind_pressure_kg_m2 : 40;

                html += `
                    <div class="p-3 rounded-lg bg-blue-50/40 border border-blue-100 hover:border-blue-200 transition" data-index="${idx}">
                        <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                            <div class="flex items-center gap-2">
                                <input type="checkbox" id="cond-enable-${c.level}" ${c.enabled ? "checked" : ""} class="cond-row-enable w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer" data-index="${idx}">
                                <label for="cond-enable-${c.level}" class="font-bold text-slate-800 cursor-pointer select-none">
                                    Conductor C${c.level}${labelSuffix}
                                </label>
                            </div>
                            <div class="flex items-center gap-2 text-slate-600">
                                <span id="cond-tension-badge-${c.level}" class="font-semibold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded text-[11px]">T: 0 kg</span>
                                <span id="cond-moment-${c.level}" class="font-semibold text-blue-800 bg-blue-100 border border-blue-300 px-2 py-0.5 rounded text-[11px]">-</span>
                                <button type="button" class="btn-remove-cond p-1 rounded hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition cursor-pointer ml-1" data-index="${idx}" title="Remove this conductor" ${count <= 1 ? "disabled style='visibility: hidden;'" : ""}>
                                    <i class="fa-solid fa-trash-can text-[11px]"></i>
                                </button>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-12 gap-2">
                            <div class="col-span-2 sm:col-span-4 lg:col-span-3">
                                <label class="block text-slate-500 mb-1">Select Conductor (SQL DB):</label>
                                <select id="cond-select-${c.level}" class="cond-row-select w-full rounded border-slate-300 py-1 px-2 font-medium bg-white text-xs cursor-pointer" data-index="${idx}">
                                    ${buildConductorSelectOptionsHtml(c.code)}
                                </select>
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-1">
                                <label class="block text-slate-500 mb-1 font-bold text-indigo-900">Qty:</label>
                                <input type="number" id="cond-num-${c.level}" value="${c.num_conductors || 2}" min="1" max="10" step="1" class="cond-row-num w-full rounded border-indigo-300 py-1 px-1.5 text-xs font-bold text-center text-indigo-950 bg-indigo-50/40" data-index="${idx}">
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-1">
                                <label class="block text-slate-500 mb-1">Height:</label>
                                <input type="number" id="cond-height-${c.level}" value="${c.height_m}" step="0.1" class="cond-row-height w-full rounded border-slate-300 py-1 px-1.5 text-xs font-semibold text-center" data-index="${idx}">
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-2">
                                <label class="block text-slate-500 mb-1 font-bold text-blue-900">Span (m):</label>
                                <input type="number" id="cond-span-${c.level}" value="${c.span_m !== undefined ? c.span_m : 40}" step="1" min="1" class="cond-row-span w-full rounded border-blue-300 py-1 px-2 text-xs font-bold text-blue-900 bg-blue-50/40 text-center" data-index="${idx}">
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-2">
                                <label class="block text-slate-500 mb-1 font-bold text-blue-900">Sag (m):</label>
                                <input type="number" id="cond-sag-${c.level}" value="${c.sag_m !== undefined ? c.sag_m : 0.14}" step="0.01" min="0.01" class="cond-row-sag w-full rounded border-blue-300 py-1 px-2 text-xs font-bold text-blue-900 bg-blue-50/40 text-center" data-index="${idx}">
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-2">
                                <label class="block text-slate-500 mb-1 font-bold text-blue-900">Wind (kg/m²):</label>
                                <input type="number" id="cond-wind-${c.level}" value="${windVal}" min="0" step="5" class="cond-row-wind w-full rounded border-blue-300 py-1 px-2 text-xs font-bold text-center text-blue-900 bg-blue-50/40" data-index="${idx}">
                            </div>
                            <div class="col-span-1 sm:col-span-2 lg:col-span-1">
                                <label class="block text-slate-500 mb-1">Angle:</label>
                                <input type="number" id="cond-angle-${c.level}" value="${c.deviation_angle_deg || 0}" step="1" class="cond-row-angle w-full rounded border-slate-300 py-1 px-1 text-xs font-medium text-center" data-index="${idx}">
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;

            // Attach event listeners
            container.querySelectorAll(".cond-row-enable").forEach(chk => {
                chk.addEventListener("change", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].enabled = e.target.checked;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-select").forEach(sel => {
                sel.addEventListener("change", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        const opt = e.target.selectedOptions[0];
                        if (opt && opt.dataset.conductor) {
                            const cData = JSON.parse(opt.dataset.conductor);
                            appState.conductors[i].code = cData.code;
                            appState.conductors[i].name = cData.name;
                            appState.conductors[i].breaking_strength_kg = cData.breaking_strength_kg;
                            appState.conductors[i].weight_kg_per_m = cData.weight_kg_per_m;
                            appState.conductors[i].overall_diameter_mm = cData.overall_diameter_mm;
                            runCalculation();
                        }
                    }
                });
            });

            container.querySelectorAll(".cond-row-num").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].num_conductors = Math.max(1, parseInt(e.target.value) || 1);
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-height").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].height_m = parseFloat(e.target.value) || 0;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-span").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].span_m = Math.max(1.0, parseFloat(e.target.value) || 1.0);
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-sag").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].sag_m = Math.max(0.01, parseFloat(e.target.value) || 0.01);
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-wind").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].wind_pressure_kg_m2 = Math.max(0, parseFloat(e.target.value) || 0);
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".cond-row-angle").forEach(inp => {
                inp.addEventListener("input", (e) => {
                    const i = parseInt(e.target.dataset.index);
                    if (appState.conductors[i]) {
                        appState.conductors[i].deviation_angle_deg = parseFloat(e.target.value) || 0;
                        runCalculation();
                    }
                });
            });

            container.querySelectorAll(".btn-remove-cond").forEach(btn => {
                btn.addEventListener("click", () => {
                    const i = parseInt(btn.dataset.index);
                    removeConductor(i);
                });
            });
        };

        function addConductor() {
            const count = appState.conductors.length;
            let newHeight = 12.0;
            if (count > 0) {
                const lowestHeight = Math.min(...appState.conductors.map(c => c.height_m));
                if (lowestHeight > 3.0) {
                    newHeight = Math.max(2.0, parseFloat((lowestHeight - 2.0).toFixed(2)));
                } else {
                    newHeight = Math.max(1.5, parseFloat((lowestHeight * 0.8).toFixed(2)));
                }
            }
            const lastC = count > 0 ? appState.conductors[count - 1] : null;
            const newCond = {
                level: count + 1,
                enabled: true,
                height_m: newHeight,
                code: lastC ? lastC.code : "AAC-400",
                name: lastC ? lastC.name : "AAC 400 sq.mm",
                breaking_strength_kg: lastC ? lastC.breaking_strength_kg : 6680.0,
                weight_kg_per_m: lastC ? lastC.weight_kg_per_m : 1.100,
                overall_diameter_mm: lastC ? lastC.overall_diameter_mm : 26.0,
                tension_mode: "sag_span",
                span_m: lastC ? lastC.span_m : 40.0,
                sag_m: lastC ? lastC.sag_m : 0.14,
                num_conductors: lastC ? lastC.num_conductors : 2,
                wind_pressure_kg_m2: (lastC && lastC.wind_pressure_kg_m2 !== undefined) ? lastC.wind_pressure_kg_m2 : 40.0,
                deviation_angle_deg: lastC ? lastC.deviation_angle_deg : 0.0
            };

            appState.conductors.push(newCond);
            renderConductorInputs();
            runCalculation();
        }

        function removeConductor(index) {
            if (appState.conductors.length <= 1) return;
            appState.conductors.splice(index, 1);
            appState.conductors.forEach((c, idx) => {
                c.level = idx + 1;
            });
            renderConductorInputs();
            runCalculation();
        }

        // Add Conductor Button
        const btnAddConductor = document.getElementById("btn-add-conductor");
        if (btnAddConductor) {
            btnAddConductor.addEventListener("click", () => {
                addConductor();
            });
        }

        // Initial render of conductor inputs
        renderConductorInputs();
    }

    // Attach Event Handlers for Pole geometry inputs
    function setupPoleInputs() {
        const heightInput = document.getElementById("pole-height-input");
        const embedInput = document.getElementById("pole-embedment-input");
        const weightInput = document.getElementById("pole-weight-input");

        if (heightInput) {
            heightInput.value = appState.pole.height_m;
            heightInput.addEventListener("input", (e) => {
                appState.pole.height_m = parseFloat(e.target.value) || 14.3;
                runCalculation();
            });
        }
        if (embedInput) {
            embedInput.value = appState.pole.embedment_m;
            embedInput.addEventListener("input", (e) => {
                appState.pole.embedment_m = parseFloat(e.target.value) || 2.0;
                runCalculation();
            });
        }
        if (weightInput) {
            weightInput.value = appState.pole.weight_kg;
            weightInput.addEventListener("input", (e) => {
                appState.pole.weight_kg = parseFloat(e.target.value) || 1200;
                runCalculation();
            });
        }
    }

    // Modal & Conductor Database Manager UI
    function setupDBManagerModal() {
        const openBtn = document.getElementById("btn-open-db-modal");
        const closeBtn = document.getElementById("btn-close-db-modal");
        const modal = document.getElementById("db-modal");
        const searchInput = document.getElementById("db-search-input");
        const typeFilter = document.getElementById("db-type-filter");
        const resetBtn = document.getElementById("btn-reset-db");
        const addBtn = document.getElementById("btn-show-add-conductor");
        const formContainer = document.getElementById("conductor-form-container");
        const condForm = document.getElementById("conductor-form");
        const cancelFormBtn = document.getElementById("btn-cancel-conductor-form");

        if (openBtn && modal) {
            openBtn.addEventListener("click", () => {
                modal.classList.remove("hidden");
                renderDBTable();
            });
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener("click", () => {
                modal.classList.add("hidden");
                if (formContainer) formContainer.classList.add("hidden");
            });
        }

        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                renderDBTable(e.target.value, typeFilter ? typeFilter.value : "");
            });
        }

        if (typeFilter) {
            typeFilter.addEventListener("change", (e) => {
                renderDBTable(searchInput ? searchInput.value : "", e.target.value);
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener("click", async () => {
                await ConductorDB.resetToDefaults();
                renderDBTable();
            });
        }

        if (addBtn && formContainer) {
            addBtn.addEventListener("click", () => {
                formContainer.classList.remove("hidden");
                if (condForm) condForm.reset();
                document.getElementById("cond-form-id").value = "";
                document.getElementById("cond-form-title").textContent = "Add New Conductor to SQL DB";
            });
        }

        if (cancelFormBtn && formContainer) {
            cancelFormBtn.addEventListener("click", () => {
                formContainer.classList.add("hidden");
            });
        }

        if (condForm) {
            condForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const condId = document.getElementById("cond-form-id").value;
                const isEdit = Boolean(condId);

                const data = {
                    code: document.getElementById("cond-form-code").value,
                    name: document.getElementById("cond-form-name").value,
                    conductor_type: document.getElementById("cond-form-type").value,
                    cross_section_sqmm: parseFloat(document.getElementById("cond-form-area").value),
                    overall_diameter_mm: parseFloat(document.getElementById("cond-form-diam").value),
                    weight_kg_per_m: parseFloat(document.getElementById("cond-form-weight").value),
                    breaking_strength_kg: parseFloat(document.getElementById("cond-form-rts").value),
                    standard: document.getElementById("cond-form-std").value,
                    notes: document.getElementById("cond-form-notes").value
                };

                const res = await ConductorDB.saveConductor(data, isEdit, condId);
                if (res.success) {
                    formContainer.classList.add("hidden");
                    renderDBTable();
                    alert(isEdit ? "Conductor updated successfully!" : "Conductor added successfully!");
                } else {
                    alert("Error: " + res.error);
                }
            });
        }

        async function renderDBTable(search = "", type = "") {
            const tbody = document.getElementById("db-table-body");
            if (!tbody) return;

            const conductors = await ConductorDB.fetchConductors(search, type);
            let html = "";
            conductors.forEach(c => {
                html += `
                    <tr class="hover:bg-slate-50 border-b border-slate-100 text-sm">
                        <td class="py-2 px-3 font-semibold text-slate-900">${c.code}</td>
                        <td class="py-2 px-3 text-slate-700">${c.name}</td>
                        <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">${c.conductor_type}</span></td>
                        <td class="py-2 px-3 text-right">${c.cross_section_sqmm.toFixed(1)}</td>
                        <td class="py-2 px-3 text-right">${c.overall_diameter_mm.toFixed(1)}</td>
                        <td class="py-2 px-3 text-right">${c.weight_kg_per_m.toFixed(3)}</td>
                        <td class="py-2 px-3 text-right font-bold text-slate-800">${Math.round(c.breaking_strength_kg).toLocaleString()}</td>
                        <td class="py-2 px-3 text-center text-xs text-slate-500">${c.standard || '-'}</td>
                        <td class="py-2 px-3 text-center">
                            <button class="btn-edit-cond text-blue-600 hover:text-blue-800 mr-2 text-xs font-medium" data-id="${c.id}">Edit</button>
                            <button class="btn-del-cond text-rose-600 hover:text-rose-800 text-xs font-medium" data-id="${c.id}">Delete</button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html || `<tr><td colspan="9" class="text-center py-6 text-slate-400">No conductors found matching criteria</td></tr>`;

            // Attach edit / delete listeners
            tbody.querySelectorAll(".btn-del-cond").forEach(btn => {
                btn.addEventListener("click", async (e) => {
                    const id = e.target.dataset.id;
                    if (await ConductorDB.deleteConductor(id)) {
                        renderDBTable();
                    }
                });
            });

            tbody.querySelectorAll(".btn-edit-cond").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    const id = e.target.dataset.id;
                    const c = conductors.find(item => item.id == id);
                    if (!c) return;

                    document.getElementById("cond-form-id").value = c.id;
                    document.getElementById("cond-form-code").value = c.code;
                    document.getElementById("cond-form-name").value = c.name;
                    document.getElementById("cond-form-type").value = c.conductor_type;
                    document.getElementById("cond-form-area").value = c.cross_section_sqmm;
                    document.getElementById("cond-form-diam").value = c.overall_diameter_mm;
                    document.getElementById("cond-form-weight").value = c.weight_kg_per_m;
                    document.getElementById("cond-form-rts").value = c.breaking_strength_kg;
                    document.getElementById("cond-form-std").value = c.standard || "PEA/TIS";
                    document.getElementById("cond-form-notes").value = c.notes || "";
                    document.getElementById("cond-form-title").textContent = `Edit Conductor (${c.code})`;

                    formContainer.classList.remove("hidden");
                });
            });
        }
    }

    // Refresh UI dropdowns when database changes
    window.addEventListener("conductors-updated", async () => {
        cachedConductors = await ConductorDB.fetchConductors();
        populateConductorSelects();
        runCalculation();
    });

    // Preset configurations
    const presetBtnStandard = document.getElementById("btn-preset-standard");
    const presetBtnHeavy = document.getElementById("btn-preset-heavy");

    if (presetBtnStandard) {
        presetBtnStandard.addEventListener("click", () => {
            appState.pole.height_m = 22.0;
            appState.pole.embedment_m = 2.8;
            appState.pole.weight_kg = 3500.0;
            document.getElementById("pole-height-input").value = 22.0;
            document.getElementById("pole-embedment-input").value = 2.8;
            document.getElementById("pole-weight-input").value = 3500;

            appState.anchor.distance_m = 12.0;
            document.getElementById("global-anchor-dist").value = 12.0;
            const slider = document.getElementById("global-anchor-dist-slider");
            if (slider) slider.value = 12;

            const standardHeights = [18.5, 16.5, 14.5, 12.5, 10.5, 8.5, 6.5];
            appState.guy_wires = standardHeights.map((h, idx) => ({
                level: idx + 1,
                enabled: true,
                height_m: h,
                anchor_distance_m: 12.0,
                size_sqmm: idx === 0 ? 50.0 : 95.0
            }));

            renderGuyWireInputs();

            const condHeights = [18.5, 16.5, 14.5];
            appState.conductors = condHeights.map((h, idx) => ({
                level: idx + 1,
                enabled: true,
                height_m: h,
                code: "AAC-400",
                name: "AAC 400 sq.mm",
                breaking_strength_kg: 6680.0,
                weight_kg_per_m: 1.100,
                overall_diameter_mm: 26.0,
                num_conductors: 2,
                span_m: 40.0,
                sag_m: 0.14,
                wind_pressure_kg_m2: 40.0,
                deviation_angle_deg: 0.0
            }));
            renderConductorInputs();

            if (appState.overhead_ground_wire) {
                appState.overhead_ground_wire.enabled = true;
                appState.overhead_ground_wire.code = "GSW-35";
                appState.overhead_ground_wire.name = "35 sq.mm Galvanized Steel Strand";
                appState.overhead_ground_wire.weight_kg_per_m = 0.272;
                appState.overhead_ground_wire.breaking_strength_kg = 2330.0;
                appState.overhead_ground_wire.overall_diameter_mm = 7.5;
                appState.overhead_ground_wire.height_m = 19.1;
                appState.overhead_ground_wire.num_conductors = 1;
                appState.overhead_ground_wire.span_m = 40.0;
                appState.overhead_ground_wire.sag_m = 0.10;
                appState.overhead_ground_wire.wind_pressure_kg_m2 = 40.0;
                const ohgwChk = document.getElementById("ohgw-enable");
                const ohgwSpec = document.getElementById("ohgw-spec-select");
                const ohgwH = document.getElementById("ohgw-height");
                const ohgwN = document.getElementById("ohgw-num");
                const ohgwSp = document.getElementById("ohgw-span");
                const ohgwSg = document.getElementById("ohgw-sag");
                const ohgwWindEl = document.getElementById("ohgw-wind");
                if (ohgwChk) ohgwChk.checked = true;
                if (ohgwSpec) ohgwSpec.value = "GSW-35";
                if (ohgwH) ohgwH.value = 19.1;
                if (ohgwN) ohgwN.value = 1;
                if (ohgwSp) ohgwSp.value = 40;
                if (ohgwSg) ohgwSg.value = 0.10;
                if (ohgwWindEl) ohgwWindEl.value = 40;
            }

            const quickSpanEl = document.getElementById("quick-span-all");
            const quickSagEl = document.getElementById("quick-sag-all");
            if (quickSpanEl) quickSpanEl.value = 40;
            if (quickSagEl) quickSagEl.value = 0.14;

            const quickWindEl = document.getElementById("quick-wind-all");
            if (quickWindEl) quickWindEl.value = 40;

            runCalculation();
        });
    }

    if (presetBtnHeavy) {
        presetBtnHeavy.addEventListener("click", () => {
            appState.pole.height_m = 22.0;
            appState.pole.embedment_m = 2.8;
            appState.pole.weight_kg = 3500.0;
            document.getElementById("pole-height-input").value = 22.0;
            document.getElementById("pole-embedment-input").value = 2.8;
            document.getElementById("pole-weight-input").value = 3500;

            appState.anchor.distance_m = 15.0;
            document.getElementById("global-anchor-dist").value = 15.0;
            const slider = document.getElementById("global-anchor-dist-slider");
            if (slider) slider.value = 15;

            const standardHeights = [18.5, 16.5, 14.5, 12.5, 10.5, 8.5, 6.5];
            appState.guy_wires = standardHeights.map((h, idx) => ({
                level: idx + 1,
                enabled: true,
                height_m: h,
                anchor_distance_m: 15.0,
                size_sqmm: idx === 0 ? 50.0 : 95.0
            }));

            renderGuyWireInputs();

            // Heavy conductors: 2 bundled conductors per phase (Qty: 2), 75m span, 0.65m sag, 40 kg/m2 wind
            const condHeights = [18.5, 16.5, 14.5];
            appState.conductors = condHeights.map((h, idx) => {
                const prev = (appState.conductors && appState.conductors[idx]) || {};
                return {
                    level: idx + 1,
                    enabled: true,
                    height_m: h,
                    code: prev.code || "AAC-400",
                    name: prev.name || "AAC 400 sq.mm",
                    breaking_strength_kg: prev.breaking_strength_kg || 6680.0,
                    weight_kg_per_m: prev.weight_kg_per_m || 1.100,
                    overall_diameter_mm: prev.overall_diameter_mm || 26.0,
                    num_conductors: 2,
                    span_m: 75.0,
                    sag_m: 0.65,
                    wind_pressure_kg_m2: 40.0,
                    deviation_angle_deg: prev.deviation_angle_deg || 0.0
                };
            });
            renderConductorInputs();

            if (appState.overhead_ground_wire) {
                appState.overhead_ground_wire.enabled = true;
                appState.overhead_ground_wire.height_m = 19.1;
                appState.overhead_ground_wire.num_conductors = 1;
                appState.overhead_ground_wire.span_m = 75.0;
                appState.overhead_ground_wire.sag_m = 0.55;
                appState.overhead_ground_wire.wind_pressure_kg_m2 = 40.0;
                const ohgwChk = document.getElementById("ohgw-enable");
                const ohgwH = document.getElementById("ohgw-height");
                const ohgwN = document.getElementById("ohgw-num");
                const ohgwSp = document.getElementById("ohgw-span");
                const ohgwSg = document.getElementById("ohgw-sag");
                const ohgwWindEl = document.getElementById("ohgw-wind");
                if (ohgwChk) ohgwChk.checked = true;
                if (ohgwH) ohgwH.value = 19.1;
                if (ohgwN) ohgwN.value = 1;
                if (ohgwSp) ohgwSp.value = 75;
                if (ohgwSg) ohgwSg.value = 0.55;
                if (ohgwWindEl) ohgwWindEl.value = 40;
            }

            const quickWindEl = document.getElementById("quick-wind-all");
            if (quickWindEl) quickWindEl.value = 40;

            runCalculation();
        });
    }

    // Print / Export Report
    const printBtn = document.getElementById("btn-print-report");
    if (printBtn) {
        printBtn.addEventListener("click", () => {
            window.print();
        });
    }

    // Startup
    setupPoleInputs();
    setupGuyWireInputs();
    setupConductorInputs();
    setupDBManagerModal();
    await initConductors();
    runCalculation();
});
