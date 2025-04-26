"use client"

import {ProfileChat} from "@/app/[pageId]/profile-creation/ProfileChat";

const TestChatPage = ({params: {pageId}}: {params: {pageId: string}}) =>
    <ProfileChat pageId={pageId}/>

export default TestChatPage;