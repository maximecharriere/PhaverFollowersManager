# PhaverFollowersManager

This repo propose Python scrypts to interact with the Phaver's GraphQl API, in order to manage followers. [Phaver](https://phaver.com/) is a Web3 Social Media based on [Lens Protocol](https://www.lens.xyz/).  
These scripts can:  

   ✅Get your private access token from Firebase  
   ✅Request Followers list  
   ✅Request Followings list  
   ✅Request all public data of a user (Points, Level, Badge, Verification, Followers/Followings number)  
   ✅Request Lens onchain quotas  
   ✅Save Followers & Followings Database in csv file  
   ✅Unfollow all users matching criterias (e.g. Points, Level, Badge, Verification, Followers/Followings       number)  
   ⬜Follow users based on criterias (e.g. Community)  

# Environment Variable to set

In order for the scripts to work, some environment variables have to be set. These variable can be put in a `.env` file in the root of the project.

| Name | Description | Common value |
|----------|----------|----------|
| PHAVER_GRAPHQL_ENDPOINT | URL of the Phaver GraphQl Endpoint | https://gql.next.phaver.com/v1/graphql |
| PHAVER_PROFILE_ID | ID of your personal profile | Scanned from Phaver App traffic |
| FIREBASE_API_URL | URL of the Firebase API to get the personal access token | https://securetoken.googleapis.com/v1/token?key= |
| FIREBASE_API_KEY | Firebase API Key of Phaver | Scanned from Phaver App traffic |
| FIREBASE_REFRESH_TOKEN | The long-term user login token | Scanned from Phaver App traffic |

# How to scan the Phaver App traffic

Here are the steps you need to follow to obtain the different IDs, KEYs and TOKENs to make these scripts work. It won't be easy, but it's necessary:  

1. Download the Phaver APK from the official website: https://www.phaver.com/android
2. Remove the Phaver APK's Man-in-the-Middle (MITM) protection with `apk-mitm`
   - Tool website: https://github.com/shroudedcode/apk-mitm
   - Complete guide: https://towardsdatascience.com/data-scraping-android-apps-b15b93aa23aa
   - Run: `apk-mitm .\phaver_1674140589.apk`
3. Launch a proxy to analyze Phaver's traffic using `mitmweb`
   - Tool website: https://mitmproxy.org/
   - Complete guide: https://medium.com/hackernoon/intercept-https-traffic-on-a-android-emulator-46023f17f6b3
   - Run *(this command add the timestamp column)*: `mitmweb --set web_columns="timestamp" --set web_columns="tls" --set web_columns="icon" --set web_columns="path" --set web_columns="method" --set web_columns="status" --set web_columns="size" --set web_columns="time"`  
   
1. Run Phaver in Android Studio (AS)
   - In AS, launch the emulator: Go to `Projects` > Three dots (top-right corner) > `Virtual Devices Manager` > `Pixel 8 Pro API 35 Patched` > `Run`
2. Perform actions in the Phaver app to generate traffic
3. Intercept requests to the Phaver and Firebase APIs to retrieve the missing information