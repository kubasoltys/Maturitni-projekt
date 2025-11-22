let karta_pocet = 0;
let gol_pocet = 0;

function pridatGol() {
    gol_pocet++;
    document.getElementById("pocet_golu").value = gol_pocet;

    const wrapper = document.getElementById("goly_wrapper");

    const block = document.createElement("div");
    block.className = "p-4 border rounded-2xl bg-gray-50 shadow-inner";

    block.innerHTML = `
        <p class="font-semibold mb-2">Gól #${gol_pocet}</p>

        <label class="block text-gray-700 font-medium mb-1">Střelec</label>
        <select name="gol_hrac_${gol_pocet}" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 mb-2">
            <option value="">-- vyber hráče --</option>
            {% for hrac in hraci %}
                <option value="{{ hrac.id }}">
                    {% if hrac.first_name and hrac.last_name %}
                        {{ hrac.first_name }} {{ hrac.last_name }}
                    {% elif hrac.first_name %}
                        {{ hrac.first_name }}
                    {% elif hrac.last_name %}
                        {{ hrac.last_name }}
                    {% else %}
                        (bez jména)
                    {% endif %}
                </option>
            {% endfor %}
        </select>

        <label class="block text-gray-700 font-medium mb-1">Minuta</label>
        <input type="text" name="gol_minuta_${gol_pocet}" placeholder="např. 12" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 mb-2">

        <label class="block text-gray-700 font-medium mb-1">Typ gólu</label>
        <select name="gol_typ_${gol_pocet}" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 mb-2">
            <option value="">-- vyber typ gólu --</option>
            <option value="normalni">Normální</option>
            <option value="penalta">Penalta</option>
            <option value="primak">Přímý kop</option>
            <option value="vlastni">Vlastní gól</option>
        </select>
    `;

    wrapper.appendChild(block);
}

function pridatKartu() {
    karta_pocet++;
    document.getElementById("pocet_karet").value = karta_pocet;

    const wrapper = document.getElementById("karty_wrapper");

    const block = document.createElement("div");
    block.className = "p-4 border rounded-2xl bg-red-50 shadow-inner";

    block.innerHTML = `
        <p class="font-semibold mb-2">Karta #${karta_pocet}</p>

        <label class="block text-gray-700 font-medium mb-1">Hráč</label>
        <select name="karta_hrac_${karta_pocet}" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-400 mb-2">
            <option value="">-- vyber hráče --</option>
            {% for hrac in hraci %}
                <option value="{{ hrac.id }}">
                    {% if hrac.first_name and hrac.last_name %}
                        {{ hrac.first_name }} {{ hrac.last_name }}
                    {% elif hrac.first_name %}
                        {{ hrac.first_name }}
                    {% elif hrac.last_name %}
                        {{ hrac.last_name }}
                    {% else %}
                        (bez jména)
                    {% endif %}
                </option>
            {% endfor %}
        </select>

        <label class="block text-gray-700 font-medium mb-1">Typ karty</label>
        <select name="karta_typ_${karta_pocet}" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-400 mb-2">
            <option value="">-- vyber typ --</option>
            <option value="zluta">Žlutá</option>
            <option value="cervena">Červená</option>
        </select>

        <label class="block text-gray-700 font-medium mb-1">Minuta</label>
        <input type="text" name="karta_minuta_${karta_pocet}" placeholder="např. 45" class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-400 mb-2">
    `;

    wrapper.appendChild(block);
}