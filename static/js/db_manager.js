/**
 * Conductor SQL Database Management Module.
 * Provides client-side dialog to browse, filter, add, edit, and delete conductors.
 */

window.ConductorDB = {
    conductors: [],
    
    fetchConductors: async function (search = "", type = "") {
        try {
            let url = `/api/conductors?search=${encodeURIComponent(search)}`;
            if (type && type !== "ALL") {
                url += `&type=${encodeURIComponent(type)}`;
            }
            const res = await fetch(url);
            const data = await res.json();
            if (data.success) {
                this.conductors = data.data;
                return this.conductors;
            }
            return [];
        } catch (e) {
            console.error("Failed to fetch conductors:", e);
            return [];
        }
    },

    saveConductor: async function (conductorData, isEdit = false, conductorId = null) {
        try {
            const url = isEdit ? `/api/conductors/${conductorId}` : "/api/conductors";
            const method = isEdit ? "PUT" : "POST";
            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(conductorData)
            });
            const data = await res.json();
            if (data.success) {
                await this.fetchConductors();
                window.dispatchEvent(new CustomEvent("conductors-updated"));
                return { success: true, message: data.message };
            } else {
                return { success: false, error: data.error };
            }
        } catch (e) {
            return { success: false, error: e.message };
        }
    },

    deleteConductor: async function (conductorId) {
        if (!confirm("Are you sure you want to delete this conductor from the SQL database?")) {
            return false;
        }
        try {
            const res = await fetch(`/api/conductors/${conductorId}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                await this.fetchConductors();
                window.dispatchEvent(new CustomEvent("conductors-updated"));
                return true;
            } else {
                alert("Error deleting conductor: " + data.error);
                return false;
            }
        } catch (e) {
            alert("Network error: " + e.message);
            return false;
        }
    },

    resetToDefaults: async function () {
        if (!confirm("Reset database to standard library conductors? Any custom entries will be lost.")) {
            return false;
        }
        try {
            const res = await fetch("/api/conductors/reset", { method: "POST" });
            const data = await res.json();
            if (data.success) {
                await this.fetchConductors();
                window.dispatchEvent(new CustomEvent("conductors-updated"));
                alert("Database reset successfully.");
                return true;
            }
        } catch (e) {
            alert("Error resetting database: " + e.message);
        }
        return false;
    }
};
