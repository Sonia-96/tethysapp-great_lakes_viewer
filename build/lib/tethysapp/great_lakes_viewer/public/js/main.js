$(function() {
    let map = TETHYS_MAP_VIEW.getMap();
    let layers = map.getLayers().getArray().filter(
        layer => layer.tethys_legend_title.startsWith('Lake')
    );
    layers.forEach(layer => {
        layer.getSource().getFeatures().forEach(feature => {
            let style = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'navy',
                    width: 1
                }),
                fill: new ol.style.Fill({
                    color: setColor(feature),
                    opacity: 0.2,
                }),
            })
            feature.setStyle(style);
        })
    })
})

let setColor = function(feature) {
    let country = feature.A.COUNTRY;
    let opacity = 0.5;
    if (country === "CAN") {
        return `rgba(216, 6, 33, ${opacity})`;
    }
    return `rgba(10, 49, 97, ${opacity})`;
}