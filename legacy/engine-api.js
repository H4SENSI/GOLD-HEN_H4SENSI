/* H4SENSI legacy engine interface.
 * This file deliberately contains no exploit implementation.
 * A compatible local engine may register:
 *   window.H4SENSI_LEGACY_ENGINE = {
 *     firmware: ["5.05","6.71","6.72"],
 *     entry: "..."
 *   };
 * The host only uses this object for capability/status reporting.
 */ 
(function(){
  "use strict";
  if(window.H4SENSI_LEGACY_ENGINE){
    window.dispatchEvent(new CustomEvent("h4sensi-log",{detail:{
      source:"LEGACY",message:"legacy engine interface detected"
    }}));
  }
})();