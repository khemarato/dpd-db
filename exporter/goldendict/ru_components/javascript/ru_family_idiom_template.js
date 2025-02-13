function makeFamilyIdioms_ru(data) {
    const familyIdiomList = data.family_idioms
    const lemma = data.lemma
    var html = "";

    //// header

    if (familyIdiomList.length > 1) {
        html += `<p class="heading" id="${lemma}_idiom_top_ru">перейти к: `; 
        familyIdiomList.forEach(item => {
            item = item.replace(/ /g, "_")
            html += `<a class="jump_ru" href="#${lemma}_idiom_ru_${item}">${item}</a> `;
        });
        html += `</p>`;
    };

    familyIdiomList.forEach(item => {
        fi = ru_family_idiom_json[item]
        item = item.replace(/ /g, "_")

        if (familyIdiomList.length > 1) {
            html += `<p class="heading underlined_ru overlined_ru" `
            html += `id=${lemma}_idiom_${item}>`;
            html += `<b>${fi.count}</b> идиоматических выражений, содержащих <b>${superScripter(item)}</b>`;
            html += `<a class="jump_ru" href="#${lemma}_idiom_top_ru"> ⤴</a></p>`;
        } else if (familyIdiomList.length == 1) {
            html += `<p class="heading underlined_ru" `
            html += `id=${lemma}_idiom_top>`;
            html += `<b>${fi.count}</b> идиоматическое выражение, содержащее <b>${superScripter(item)}</b>`;
        };
        
        //// table

        html += `<table class="family_ru"><tbody>`;
        fi.data.forEach(data => {
            const [word, pos, meaning, complete] = data
            html += `
                <tr>
                <th>${word}</th>
                <td><b>${pos}</b></td>
                <td>${meaning}</td>
                <td><span class="gray">${complete}</span</td>
                </tr>`;
        });

        html += `</tbody></table>`;
    });

    //// footer

    html += `
        <p class="footer_ru">
        Пожалуйста, добавьте больше идиом  
        <a class="link_ru" 
        href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&amp;entry.438735500=${lemma}&amp;entry.326955045=Идиомы&amp;entry.1433863141=GoldenDict+${data.date}" 
        target="_blank">
        здесь</a>.`; 
    
    html += `<a class="jump_ru" href="#${lemma}_idiom_top"> ⤴</a></p>`

    return html
}
