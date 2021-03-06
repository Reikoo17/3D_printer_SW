import QtQuick 2.15
import QtQuick.Controls 2.15
import "../controls"

Item {
    id: temperature_item
    CustomButton {
        id: customButton
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 10
        anchors.leftMargin: 10
    }

    Rectangle {
        id: temperatureView
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: customButton.top
        anchors.topMargin: 0
        anchors.bottomMargin: 5
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        color:"transparent"

        Column {
            id: column
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Repeater {
                id: repeater
                model: back.num_of_extruders

                Temperature_box {
                    id: temperature_box_extruder
                    name: "Extruder " + index
                    x: 0
                    y: 0
                    tool: "T" + index
                    width: 301
                    height: 120
                    visible: true
                    real_tempetature: back.extruder_temperature[index]
                    target_temperature: back.extruder_target_temperature[index]
                    max_temperature: back.extruder_max_temperature

                }
            }
            Temperature_box {
                id: temperature_box_bed
                name: "Bed"
                tool: "B"
                width: 301
                height: 120
                visible: back.bed_status
                real_tempetature: back.bed_temperature
                target_temperature: back.bed_target_temperature
                max_temperature: back.bed_max_temperature
            }

            Temperature_box {
                id: temperature_box_chamber
                name: "Chamber"
                tool: "C"
                width: 301
                height: 120
                visible: back.chamber_status
                real_tempetature: back.chamber_temperature
                max_temperature: back.chamber_max_temperature
                target_temperature: back.chamber_target_temperature
            }

        }

    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorColor:"#4c4e50";formeditorZoom:0.9;height:974;width:580}
}
##^##*/
