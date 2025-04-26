import NextAuth from "next-auth"
import FacebookProvider from "next-auth/providers/facebook";

export const authOptions = {
    providers: [
        FacebookProvider({
            clientId: process.env.FACEBOOK_CLIENT_ID,
            clientSecret: process.env.FACEBOOK_CLIENT_SECRET,
            authorization: {
                url: "https://www.facebook.com/v17.0/dialog/oauth",
                params: {
                    scope: "email public_profile pages_show_list pages_read_engagement pages_manage_posts"
                }
            }
        })
    ],
}

export default NextAuth(authOptions)
