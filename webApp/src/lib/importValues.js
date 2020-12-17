// Introduce values in html
importValues = function (html, dict) {

    for (key in dict) {

        html = html.replace(key, dict[key]);

    }

    return html

}

// Export module
module.exports = importValues;