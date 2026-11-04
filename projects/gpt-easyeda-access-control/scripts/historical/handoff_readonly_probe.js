const document=await eda.dmt_SelectControl.getCurrentDocumentInfo();return {document,pcbPartCount:document?.documentType===3?(await eda.pcb_PrimitiveComponent.getAll()).length:null};
