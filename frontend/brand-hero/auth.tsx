"use client"

import {PropsWithChildren} from "react";
import {SessionProvider} from "next-auth/react";
import {QueryClient, QueryClientProvider} from '@tanstack/react-query'

const queryClient = new QueryClient()


export const AuthProvider = ({children}: PropsWithChildren) =>
    <SessionProvider>{children}</SessionProvider>;

export const QueryProvider = ({children}: PropsWithChildren) =>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;


