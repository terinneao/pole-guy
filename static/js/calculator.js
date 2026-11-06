/**
 * Client-Side Statics Calculation Engine for Pole Guy Wires.
 * Units: kg, meter, degrees.
 */

window.PoleGuyCalculator = {
    calculate: function (state) {
        const pole = state.pole || {};
        const poleHeight = parseFloat(pole.height_m) || 14.3;
        const poleEmbedment = parseFloat(pole.embedment_m) || 2.0;
        const poleWeight = parseFloat(pole.weight_kg) || 1200.0;
        const poleAboveGround = Math.max(0, poleHeight - poleEmbedment);

        const globalAnchorDist = parseFloat(state.anchor?.distance_m) || 8.0;

        const standardGuySpecs = {
            25: { name: "25 sq.mm Galvanized Steel Strand", weight: 0.192, rts: 1647.0 },
            35: { name: "35 sq.mm Galvanized Steel Strand", weight: 0.272, rts: 2330.0 },
            50: { name: "50 sq.mm Galvanized Steel Strand", weight: 0.392, rts: 3355.0 },
            95: { name: "95 sq.mm Galvanized Steel Strand", weight: 0.764, rts: 8528.0 }
        };

        const guySpec = state.guy_wire_spec || {};
        const rawGuySize = parseFloat(guySpec.size_sqmm) || 95.0;
        const standardSizes = [25, 35, 50, 95];
        const closestGuySize = standardSizes.reduce((prev, curr) => Math.abs(curr - rawGuySize) < Math.abs(prev - rawGuySize) ? curr : prev);
        const specInfo = standardGuySpecs[closestGuySize] || standardGuySpecs[95];
        const guySize = parseFloat(guySpec.size_sqmm) || closestGuySize;
        const guyType = guySpec.name || guySpec.type || specInfo.name;
        const defaultRts = specInfo.rts;
        const defaultUnitWt = specInfo.weight;
        const guyRts = parseFloat(guySpec.rts_kg) || defaultRts;
        const guyUnitWt = parseFloat(guySpec.unit_weight_kg_m) || defaultUnitWt;
        const requiredSf = parseFloat(guySpec.required_sf) || 2.0;

        const calcMethod = state.calculation_method || "elastic";

        // Conductor calculations
        const conductors = state.conductors || [];
        const conductorResults = [];
        let totalConductorHForce = 0;
        let totalOverturningMoment = 0;
        let totalConductorWeight = 0;

        conductors.forEach((c, idx) => {
            const level = c.level || idx + 1;
            const enabled = Boolean(c.enabled);
            const height = parseFloat(c.height_m) || 0;
            const numCond = Math.max(1, parseInt(c.num_conductors) || 2);
            const rts = parseFloat(c.breaking_strength_kg) || 6680.0;
            const unitWt = parseFloat(c.weight_kg_per_m) || 1.100;
            const diamMm = parseFloat(c.overall_diameter_mm) || 26.0;
            const spanM = Math.max(1.0, parseFloat(c.span_m) || parseFloat(c.span_length_m) || 40);
            const sagM = Math.max(0.01, parseFloat(c.sag_m) || 0.14);
            const windP = Math.max(0, parseFloat(c.wind_pressure_kg_m2) || 0);
            const angleDeg = parseFloat(c.deviation_angle_deg) || 0;

            const wWind = windP * (diamMm / 1000.0);
            const wResultant = Math.sqrt(unitWt * unitWt + wWind * wWind);

            let singleTension = 0;
            if (c.tension_mode === "direct") {
                singleTension = parseFloat(c.tension_kg) || 0;
            } else if (c.tension_mode === "ratio") {
                const ratio = parseFloat(c.tension_ratio) || 0.2;
                singleTension = rts * ratio;
            } else {
                // Default: Parabolic sag-tension with resultant weight T = (w_r * S^2) / (8 * sag)
                singleTension = (wResultant * (spanM * spanM)) / (8.0 * sagM);
            }
            const tensionPctRts = rts > 0 ? (singleTension / rts) * 100.0 : 0.0;

            if (!enabled) {
                conductorResults.push({
                    level: level,
                    enabled: false,
                    height_m: height,
                    code: c.code || "DISABLED",
                    name: c.name || "Disabled",
                    weight_kg_per_m: Number(unitWt.toFixed(4)),
                    overall_diameter_mm: Number(diamMm.toFixed(2)),
                    tension_per_cond_kg: 0,
                    horizontal_force_kg: 0,
                    vertical_weight_kg: 0,
                    moment_kg_m: 0,
                    num_conductors: numCond,
                    wind_pressure_kg_m2: Number(windP.toFixed(1)),
                    wind_load_kg_per_m: Number(wWind.toFixed(4)),
                    resultant_weight_kg_m: Number(wResultant.toFixed(4))
                });
                return;
            }

            let fTurn = 0;
            if (Math.abs(angleDeg) > 1e-4) {
                const rad = (Math.abs(angleDeg) / 2.0) * (Math.PI / 180.0);
                fTurn = 2.0 * singleTension * Math.sin(rad) * numCond;
            } else {
                fTurn = singleTension * numCond;
            }

            let fWind = 0;
            if (windP > 0) {
                const areaProj = (diamMm / 1000.0) * (spanM / 2.0) * numCond;
                const angleRad = (angleDeg / 2.0) * (Math.PI / 180.0);
                fWind = windP * areaProj * Math.cos(angleRad);
            }

            const hForce = fTurn + fWind;
            const vWeight = unitWt * (spanM / 2.0) * numCond;
            const levelMoment = hForce * height;

            totalConductorHForce += hForce;
            totalOverturningMoment += levelMoment;
            totalConductorWeight += vWeight;

            conductorResults.push({
                level: level,
                enabled: true,
                height_m: Number(height.toFixed(2)),
                code: c.code || "AAC-400",
                name: c.name || "Conductor",
                weight_kg_per_m: Number(unitWt.toFixed(4)),
                overall_diameter_mm: Number(diamMm.toFixed(2)),
                span_m: Number(spanM.toFixed(2)),
                sag_m: Number(sagM.toFixed(3)),
                wind_pressure_kg_m2: Number(windP.toFixed(1)),
                wind_load_kg_per_m: Number(wWind.toFixed(4)),
                resultant_weight_kg_m: Number(wResultant.toFixed(4)),
                single_tension_kg: Number(singleTension.toFixed(2)),
                tension_per_cond_kg: Number(singleTension.toFixed(2)),
                tension_pct_rts: Number(tensionPctRts.toFixed(1)),
                horizontal_force_kg: Number(hForce.toFixed(2)),
                vertical_weight_kg: Number(vWeight.toFixed(2)),
                moment_kg_m: Number(levelMoment.toFixed(2)),
                num_conductors: numCond,
                rts_kg: rts,
                deviation_angle_deg: angleDeg
            });
        });

        // Overhead Ground Wire (OHGW - installed over top conductor)
        const rawOhgw = state.overhead_ground_wire || state.ohgw || {};
        const ohgwEnabled = Boolean(rawOhgw.enabled);
        const ohgwHeight = parseFloat(rawOhgw.height_m) || 19.1;
        const ohgwNum = Math.max(1, parseInt(rawOhgw.num_conductors) || parseInt(rawOhgw.num_wires) || 1);
        const standardOhgwSpecs = {
            "GSW-25": { name: "25 sq.mm Galvanized Steel Strand", weight: 0.192, rts: 1647.0, diam: 6.3 },
            "GSW-35": { name: "35 sq.mm Galvanized Steel Strand", weight: 0.272, rts: 2330.0, diam: 7.5 },
            "GSW-50": { name: "50 sq.mm Galvanized Steel Strand", weight: 0.392, rts: 3355.0, diam: 9.0 },
            "GSW-95": { name: "95 sq.mm Galvanized Steel Strand", weight: 0.764, rts: 8528.0, diam: 12.5 },
            "ACSR-50": { name: "ACSR 50 sq.mm", weight: 0.187, rts: 1480.0, diam: 9.6 }
        };
        const ohgwCode = rawOhgw.code || "GSW-35";
        const specOhgw = standardOhgwSpecs[ohgwCode] || standardOhgwSpecs["GSW-35"];
        const ohgwName = rawOhgw.name || specOhgw.name;
        const ohgwUnitWt = parseFloat(rawOhgw.weight_kg_per_m) || specOhgw.weight;
        const ohgwRts = parseFloat(rawOhgw.breaking_strength_kg) || specOhgw.rts;
        const ohgwDiamMm = parseFloat(rawOhgw.overall_diameter_mm) || specOhgw.diam;
        const ohgwSpanM = Math.max(1.0, parseFloat(rawOhgw.span_m) || 40.0);
        const ohgwSagM = Math.max(0.01, parseFloat(rawOhgw.sag_m) || 0.50);
        const ohgwWindP = Math.max(0, parseFloat(rawOhgw.wind_pressure_kg_m2) || 0.0);
        const ohgwAngleDeg = parseFloat(rawOhgw.deviation_angle_deg) || 0.0;

        const ohgwWWind = ohgwWindP * (ohgwDiamMm / 1000.0);
        const ohgwWResultant = Math.sqrt(ohgwUnitWt * ohgwUnitWt + ohgwWWind * ohgwWWind);

        let ohgwSingleT = 0;
        if (rawOhgw.tension_mode === "direct") {
            ohgwSingleT = parseFloat(rawOhgw.tension_kg) || 245.0;
        } else if (rawOhgw.tension_mode === "ratio") {
            const ratio = parseFloat(rawOhgw.tension_ratio) || 0.15;
            ohgwSingleT = ohgwRts * ratio;
        } else {
            // sag_span with resultant weight T = (w_r * S^2) / (8 * sag)
            ohgwSingleT = (ohgwWResultant * (ohgwSpanM * ohgwSpanM)) / (8.0 * ohgwSagM);
        }

        const ohgwPctRts = ohgwRts > 0 ? (ohgwSingleT / ohgwRts * 100.0) : 0.0;
        let ohgwResult = null;

        if (!ohgwEnabled) {
            ohgwResult = {
                enabled: false,
                height_m: Number(ohgwHeight.toFixed(2)),
                code: ohgwCode,
                name: ohgwName,
                weight_kg_per_m: Number(ohgwUnitWt.toFixed(4)),
                breaking_strength_kg: Number(ohgwRts.toFixed(2)),
                overall_diameter_mm: Number(ohgwDiamMm.toFixed(2)),
                span_m: Number(ohgwSpanM.toFixed(2)),
                sag_m: Number(ohgwSagM.toFixed(3)),
                wind_pressure_kg_m2: Number(ohgwWindP.toFixed(1)),
                wind_load_kg_per_m: Number(ohgwWWind.toFixed(4)),
                resultant_weight_kg_m: Number(ohgwWResultant.toFixed(4)),
                single_tension_kg: Number(ohgwSingleT.toFixed(2)),
                tension_pct_rts: Number(ohgwPctRts.toFixed(1)),
                horizontal_force_kg: 0,
                vertical_weight_kg: 0,
                moment_kg_m: 0,
                num_conductors: ohgwNum,
                rts_kg: ohgwRts,
                deviation_angle_deg: ohgwAngleDeg
            };
        } else {
            let ohgwFTurn = 0;
            if (Math.abs(ohgwAngleDeg) > 1e-4) {
                const rad = (Math.abs(ohgwAngleDeg) / 2.0) * (Math.PI / 180.0);
                ohgwFTurn = 2.0 * ohgwSingleT * Math.sin(rad) * ohgwNum;
            } else {
                ohgwFTurn = ohgwSingleT * ohgwNum;
            }

            let ohgwFWind = 0;
            if (ohgwWindP > 0) {
                const proj = (ohgwDiamMm / 1000.0) * (ohgwSpanM / 2.0) * ohgwNum;
                ohgwFWind = ohgwWindP * proj * Math.cos((ohgwAngleDeg / 2.0) * (Math.PI / 180.0));
            }

            const ohgwHForce = ohgwFTurn + ohgwFWind;
            const ohgwVWeight = ohgwUnitWt * (ohgwSpanM / 2.0) * ohgwNum;
            const ohgwMoment = ohgwHForce * ohgwHeight;

            totalConductorHForce += ohgwHForce;
            totalOverturningMoment += ohgwMoment;
            totalConductorWeight += ohgwVWeight;

            ohgwResult = {
                enabled: true,
                height_m: Number(ohgwHeight.toFixed(2)),
                code: ohgwCode,
                name: ohgwName,
                weight_kg_per_m: Number(ohgwUnitWt.toFixed(4)),
                breaking_strength_kg: Number(ohgwRts.toFixed(2)),
                overall_diameter_mm: Number(ohgwDiamMm.toFixed(2)),
                span_m: Number(ohgwSpanM.toFixed(2)),
                sag_m: Number(ohgwSagM.toFixed(3)),
                wind_pressure_kg_m2: Number(ohgwWindP.toFixed(1)),
                wind_load_kg_per_m: Number(ohgwWWind.toFixed(4)),
                resultant_weight_kg_m: Number(ohgwWResultant.toFixed(4)),
                single_tension_kg: Number(ohgwSingleT.toFixed(2)),
                tension_pct_rts: Number(ohgwPctRts.toFixed(1)),
                horizontal_force_kg: Number(ohgwHForce.toFixed(2)),
                vertical_weight_kg: Number(ohgwVWeight.toFixed(2)),
                moment_kg_m: Number(ohgwMoment.toFixed(2)),
                num_conductors: ohgwNum,
                rts_kg: ohgwRts,
                deviation_angle_deg: ohgwAngleDeg
            };
        }

        // Guy wires calculations
        const rawGuys = state.guy_wires || [];
        const activeGuys = [];
        const parsedGuys = [];

        rawGuys.forEach((g, idx) => {
            const level = g.level || idx + 1;
            const enabled = Boolean(g.enabled);
            const height = parseFloat(g.height_m) || 0;
            let anchorD = parseFloat(g.anchor_distance_m);
            if (isNaN(anchorD) || anchorD <= 0) {
                anchorD = globalAnchorDist;
            }

            const slopeLen = Math.sqrt(height * height + anchorD * anchorD);
            const angleRad = Math.atan2(height, anchorD);
            const angleDeg = angleRad * (180.0 / Math.PI);
            const cosA = anchorD / slopeLen;
            const sinA = height / slopeLen;

            // Level-specific guy wire size & properties
            const levelRawSize = parseFloat(g.size_sqmm) || guySize;
            const levelClosest = standardSizes.reduce((prev, curr) => Math.abs(curr - levelRawSize) < Math.abs(prev - levelRawSize) ? curr : prev);
            const levelSpec = standardGuySpecs[levelClosest] || standardGuySpecs[95];

            const levelSize = parseFloat(g.size_sqmm) || levelClosest;
            const levelUnitWt = parseFloat(g.unit_weight_kg_m) || levelSpec.weight;
            const defaultLevelRts = Math.abs(levelSize - guySize) < 1.0 ? guyRts : levelSpec.rts;
            const levelRts = parseFloat(g.rts_kg) || defaultLevelRts;
            const levelArea = levelSize;

            const item = {
                level: level,
                enabled: enabled,
                height_m: height,
                anchor_distance_m: anchorD,
                size_sqmm: levelSize,
                unit_weight_kg_m: levelUnitWt,
                rts_kg: levelRts,
                area_sqmm: levelArea,
                slope_length_m: slopeLen,
                angle_deg: angleDeg,
                angle_rad: angleRad,
                cos_a: cosA,
                sin_a: sinA,
                dead_weight_kg: levelUnitWt * slopeLen
            };
            parsedGuys.push(item);
            if (enabled) {
                activeGuys.push(item);
            }
        });

        const numActiveGuys = activeGuys.length;
        if (numActiveGuys > 0 && totalOverturningMoment > 0) {
            if (calcMethod === "equal_moment") {
                const momentPerGuy = totalOverturningMoment / numActiveGuys;
                activeGuys.forEach(g => {
                    const th = g.height_m > 0 ? momentPerGuy / g.height_m : 0;
                    const t = g.cos_a > 0 ? th / g.cos_a : 0;
                    g.tension_kg = t;
                    g.h_force_kg = th;
                    g.v_force_kg = t * g.sin_a;
                    g.moment_kg_m = th * g.height_m;
                });
            } else if (calcMethod === "equal_shear") {
                const thPerGuy = totalConductorHForce / numActiveGuys;
                activeGuys.forEach(g => {
                    const t = g.cos_a > 0 ? thPerGuy / g.cos_a : 0;
                    g.tension_kg = t;
                    g.h_force_kg = thPerGuy;
                    g.v_force_kg = t * g.sin_a;
                    g.moment_kg_m = thPerGuy * g.height_m;
                });
            } else {
                // Elastic deflection method with area strain compatibility
                let sumDenom = 0;
                activeGuys.forEach(g => {
                    sumDenom += (g.area_sqmm * g.height_m * g.height_m * g.cos_a * g.cos_a) / g.slope_length_m;
                });

                if (sumDenom > 1e-6) {
                    activeGuys.forEach(g => {
                        const num = (g.area_sqmm * g.height_m * g.cos_a) / g.slope_length_m;
                        const t = totalOverturningMoment * (num / sumDenom);
                        const th = t * g.cos_a;
                        const tv = t * g.sin_a;
                        const m = th * g.height_m;
                        g.tension_kg = t;
                        g.h_force_kg = th;
                        g.v_force_kg = tv;
                        g.moment_kg_m = m;
                    });
                }
            }
        }

        const guyResults = [];
        let totalGuyTension = 0;
        let totalGuyHForce = 0;
        let totalGuyVForce = 0;
        let totalResistingMoment = 0;
        let totalGuyWeight = 0;

        parsedGuys.forEach(g => {
            if (!g.enabled || numActiveGuys === 0 || totalOverturningMoment <= 0) {
                guyResults.push({
                    level: g.level,
                    enabled: Boolean(g.enabled),
                    size_sqmm: Number(g.size_sqmm.toFixed(1)),
                    rts_kg: Number(g.rts_kg.toFixed(1)),
                    height_m: Number(g.height_m.toFixed(2)),
                    anchor_distance_m: Number(g.anchor_distance_m.toFixed(2)),
                    slope_length_m: Number(g.slope_length_m.toFixed(2)),
                    angle_deg: Number(g.angle_deg.toFixed(1)),
                    tension_kg: 0,
                    horizontal_force_kg: 0,
                    vertical_force_kg: 0,
                    moment_kg_m: 0,
                    safety_factor: !g.enabled ? 999 : 0,
                    utilization_pct: 0,
                    status: !g.enabled ? "DISABLED" : "NO_LOAD",
                    dead_weight_kg: Number(g.dead_weight_kg.toFixed(2))
                });
            } else {
                const t = g.tension_kg || 0;
                const th = g.h_force_kg || 0;
                const tv = g.v_force_kg || 0;
                const m = g.moment_kg_m || 0;

                const sf = t > 1e-4 ? (g.rts_kg / t) : 999;
                const util = (t / g.rts_kg) * 100.0;

                let status = "SAFE";
                if (sf < 1.5) {
                    status = "OVERLOADED";
                } else if (sf < requiredSf) {
                    status = "WARNING";
                }

                totalGuyTension += t;
                totalGuyHForce += th;
                totalGuyVForce += tv;
                totalResistingMoment += m;
                totalGuyWeight += g.dead_weight_kg;

                guyResults.push({
                    level: g.level,
                    enabled: true,
                    size_sqmm: Number(g.size_sqmm.toFixed(1)),
                    rts_kg: Number(g.rts_kg.toFixed(1)),
                    height_m: Number(g.height_m.toFixed(2)),
                    anchor_distance_m: Number(g.anchor_distance_m.toFixed(2)),
                    slope_length_m: Number(g.slope_length_m.toFixed(2)),
                    angle_deg: Number(g.angle_deg.toFixed(1)),
                    tension_kg: Number(t.toFixed(2)),
                    horizontal_force_kg: Number(th.toFixed(2)),
                    vertical_force_kg: Number(tv.toFixed(2)),
                    moment_kg_m: Number(m.toFixed(2)),
                    safety_factor: Number(sf.toFixed(2)),
                    utilization_pct: Number(util.toFixed(1)),
                    status: status,
                    dead_weight_kg: Number(g.dead_weight_kg.toFixed(2))
                });
            }
        });

        // Anchor forces
        const anchorResultant = Math.sqrt(totalGuyHForce * totalGuyHForce + totalGuyVForce * totalGuyVForce);
        const anchorAngleDeg = totalGuyHForce > 1e-4 ? (Math.atan2(totalGuyVForce, totalGuyHForce) * 180.0 / Math.PI) : 90.0;

        // Downward vertical thrust on pole
        const totalDownwardThrust = totalGuyVForce + poleWeight + totalConductorWeight + totalGuyWeight;

        const netMoment = Math.abs(totalOverturningMoment - totalResistingMoment);
        const netHShear = totalConductorHForce - totalGuyHForce;
        const momentBalancePct = totalOverturningMoment > 1e-4 ? ((totalResistingMoment / totalOverturningMoment) * 100.0) : 100.0;

        const anyOverloaded = guyResults.some(g => g.enabled && g.status === "OVERLOADED");
        const anyWarning = guyResults.some(g => g.enabled && g.status === "WARNING");
        let overallStatus = "SAFE";
        if (anyOverloaded || numActiveGuys === 0) {
            overallStatus = anyOverloaded ? "OVERLOADED" : "UNSUPPORTED";
        } else if (anyWarning) {
            overallStatus = "WARNING";
        }

        return {
            status: overallStatus,
            calculation_method: calcMethod,
            guy_spec: {
                type: guyType,
                name: guyType,
                size_sqmm: guySize,
                rts_kg: guyRts,
                unit_weight_kg_m: guyUnitWt,
                required_sf: requiredSf
            },
            pole: {
                height_m: poleHeight,
                embedment_m: poleEmbedment,
                above_ground_m: Number(poleAboveGround.toFixed(2)),
                weight_kg: poleWeight
            },
            anchor: {
                global_distance_m: globalAnchorDist,
                total_horizontal_pull_kg: Number(totalGuyHForce.toFixed(2)),
                total_vertical_uplift_kg: Number(totalGuyVForce.toFixed(2)),
                resultant_pull_kg: Number(anchorResultant.toFixed(2)),
                resultant_angle_deg: Number(anchorAngleDeg.toFixed(1))
            },
            pole_base: {
                total_downward_thrust_kg: Number(totalDownwardThrust.toFixed(2)),
                net_horizontal_shear_kg: Number(netHShear.toFixed(2)),
                net_unbalance_moment_kg_m: Number(netMoment.toFixed(2)),
                moment_balance_pct: Number(momentBalancePct.toFixed(1))
            },
            summary: {
                total_conductor_h_force_kg: Number(totalConductorHForce.toFixed(2)),
                total_overturning_moment_kg_m: Number(totalOverturningMoment.toFixed(2)),
                total_guy_h_force_kg: Number(totalGuyHForce.toFixed(2)),
                total_resisting_moment_kg_m: Number(totalResistingMoment.toFixed(2)),
                total_conductor_weight_kg: Number(totalConductorWeight.toFixed(2)),
                total_guy_weight_kg: Number(totalGuyWeight.toFixed(2)),
                ohgw_h_force_kg: Number((ohgwResult?.horizontal_force_kg || 0).toFixed(2)),
                ohgw_moment_kg_m: Number((ohgwResult?.moment_kg_m || 0).toFixed(2)),
                active_guy_count: numActiveGuys
            },
            overhead_ground_wire: ohgwResult,
            conductors: conductorResults,
            guy_wires: guyResults
        };
    }
};
