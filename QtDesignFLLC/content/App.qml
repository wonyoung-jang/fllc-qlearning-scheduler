// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick 6.6

Window {
    width: mainScreen.width
    height: mainScreen.height

    visible: true
    title: "FLLC Q-Learning Scheduler"

    CustomSpinbox {
        id: customSpinbox
        x: 0
        y: 0
    }
}

