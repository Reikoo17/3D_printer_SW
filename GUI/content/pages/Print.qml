import QtQuick 2.15
import QtQuick.Controls 2.15
import "../controls"
import QtQuick.Dialogs 1.1

Item {
        CustomButton {
            id: customButton
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 4
            anchors.leftMargin: 4
        }

        SwipeView {
            id: printView
            height: 390
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: pageIndicator.bottom
            anchors.bottom: customButton.top
            anchors.bottomMargin: 10
            anchors.topMargin: 10
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            currentIndex: 2

            Item {
                id: print_file

                Button {
                    id: button
                    x: 382
                    y: 82
                    width: 137
                    height: 57
                    text: qsTr("Cesta")
                    onClicked: {
                        fileDialog.open()
                    }
                }

                TextField {
                    id: fileurl_textfield
                    x: 40
                    y: 96
                    width: 312
                    height: 43
                    placeholderText: qsTr("Text Field")

                }

                Button {
                    id: button1
                    x: 205
                    y: 332
                    width: 128
                    height: 68
                    text: qsTr("tisk")
                    onClicked: {
                        backend.print(fileurl_textfield.text)
                    }
                }
            }

            Item {
                id: print_automatic
            }

            Item {
                id: scripts

                ComboBox {
                    id: script_choice
                    x: 165
                    y: 8
                    width: 224
                    height: 48
                    model: back.script_list
                    Component.onCompleted: backend.getScript(script_choice.currentValue)
                    onActivated: backend.getScript(back.script_list[index])

                }

                TextArea {
                    id: script_textarea
                    x: 38
                    y: 70
                    width: 522
                    height: 747
                    placeholderText: qsTr("Text Area")
                    text: back.script_text
                }

                Button {
                    id: save_button
                    x: 256
                    y: 823
                    text: qsTr("save")
                    onClicked: backend.saveScript(script_choice.currentValue, script_textarea.text)
                }
            }


        }

        PageIndicator {
            id: pageIndicator
            width: 48
            height: 20
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 0

            count: printView.count
            currentIndex: printView.currentIndex

        }

    FileDialog {
        id: fileDialog
        title: "Please choose a G-code file"
        folder: shortcuts.home
        onAccepted: {
            var path = fileDialog.fileUrl.toString();
            path= path.replace(/^(file:\/{3})|(qrc:\/{2})|(http:\/{2})/,"");
            fileurl_textfield.text = decodeURIComponent(path);
            fileDialog.close
        }
        onRejected: {
            console.log("Canceled")
            fileDialog.close
        }
        nameFilters: [ "G-code (*.gcode *.txt)", "All files (*)" ]
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.75;height:974;width:580}
}
##^##*/
