import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "RogoAI.ASR",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "RogoAI_ExtractAudioFromVideo") {
            console.log("RogoAI Extract Audio node registered");
        }
    }
});