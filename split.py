import os

patientsList = ['Melanoma_425362-245-T/Implants_Session_1/00066326 TSE45 MR/', 'Melanoma_425362-245-T/Implants_Session_1/00066324 TSE45 MR/']
numberOfVolumnList = ['3', '3']
orderList = ['1,1,0', '1,1,1']

for i in range(len(patientsList)):
    os.system(' '.join(["python pydicom_split.py -n",
                                '"'+numberOfVolumnList[i]+'"',
                                '"'+patientsList[i]+'"',
                                '-order', '"'+orderList[i]+'"']))
    # print(' '.join(["python pydicom_split.py -n",
    #                             '"'+numberOfVolumnList[i]+'"',
    #                             '"'+patientsList[i]+'"',
    #                             '-order', '"'+orderList[i]+'"']))
