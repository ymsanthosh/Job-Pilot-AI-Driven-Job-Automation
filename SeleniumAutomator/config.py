
browser = ["Chrome"]

email = "YOUR_LINKEDIN_EMAIL"
password = "LINKEDIN_PASSWORD"

#run browser in headless mode, no browser screen will be shown it will work in background.
headless = False

chromeProfilePath = r""


#job experience Level - ex:  ["Internship", "Entry level" , "Associate" , "Mid-Senior level" , "Director" , "Executive"]
experienceLevels = [ "Entry level","Internship","Associate" ]

#job posted date - ex: ["Any Time", "Past Month" , "Past Week" , "Past 24 hours"] - select only one
datePosted = ["Past Week"]

#job type - ex:  ["Full-time", "Part-time" , "Contract" , "Temporary", "Volunteer", "Intership", "Other"]
jobType = ["Full-time", "Part-time" , "Contract"]

#remote  - ex: ["On-site" , "Remote" , "Hybrid"]
remote = ["On-site" , "Remote" , "Hybrid"]


#sort - ex:["Recent"] or ["Relevent"] - select only one
sort = ["Recent"]

#Follow companies after sucessfull application True - yes, False - no
followCompanies = False

#Below settings are for linkedin bot Pro, you can purchase monthly or yearly subscription to use them from me.
# If you have multiple CV's you can choose which one you want the bot to use. (1- the first one on the list, 2 - second , etc)
preferredCv = 1
# Output unaswered questions into a seperate text file, will output radio box, dropdown and input field questions into seperate .yaml file
outputSkippedQuestions = True
# Use AI to fill and answer skipped questions. Will cost 5 credits per answer cause of computational power.
useAiAutocomplete = False
# Only Apply these companies -  ex: ["Apple","Google"] -  leave empty for all companies
onlyApplyCompanies = []
# Only Apply titles having these keywords -  ex:["web", "remote"] - leave empty for all companies
onlyApplyTitles = [] 
#Dont apply the job posted by the Hiring member contains this in his/her name - ex: ["adam","Sarah"]
blockHiringMember = [] 
#Only apply the job sposted by the Hiring member contains this in his/her name - ex: ["adam","Sarah"]
onlyApplyHiringMember = [] 
#Only apply jobs having less than applications - ex:["100"] will apply jobs having upto 100 applications
onlyApplyMaxApplications = []
# Only apply jobs having more than applications - ex:["10"] will apply jobs having more than 10 applications
onlyApplyMinApplications = []
#Only apply jobs having these keywords in the job description
onlyApplyJobDescription = []
#Do not apply the jobs having these keywords in the job description
blockJobDescription = []
#Apply companies having equal or more than employes - ex: ["100"]
onlyAppyMimEmployee = []
#Apply the ones linkedin is saying "you may be a goodfit"
onlyApplyLinkedinRecommending = False
#Only apply the ones you have skilled badge
onlyApplySkilledBages = False
#Save the jobs by pressing SAVE button before apply  True - yes, False - no
saveBeforeApply = False
#Sent a message to the hiring manager once you apply for the role
messageToHiringManager = ""
#List and output non Easy Apply jobs links
listNonEasyApplyJobsUrl = False
#Select radio button for unsawered questions. If the bot cannot find an answer for a radio button, it will automatically select first or second option. Default radio button answer, 1 for Yes, 2 for No. Leave empty if you dont want this option.
defaultRadioOption = 1
#Check yes or no to all checkbox questions (True - yes, False - no), leave empty if you dont want this option
answerAllCheckboxes = ""
#Output file type. Can be .txt or .csv (excel)
outputFileType = [".txt"]
 # Testing & Debugging features
displayWarnings = False
