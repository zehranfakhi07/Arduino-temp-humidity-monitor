import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, TextInput, Button, FlatList, SafeAreaView, TouchableOpacity } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const API_BASE = process.env.EXPO_PUBLIC_API_BASE || 'http://localhost:8000';

async function api(path: string, method: string = 'GET', body?: any, token?: string) {
	const res = await fetch(`${API_BASE}${path}`, {
		method,
		headers: {
			'Content-Type': 'application/json',
			...(token ? { Authorization: `Bearer ${token}` } : {}),
		},
		body: body ? JSON.stringify(body) : undefined,
	});
	if (!res.ok) {
		const t = await res.text();
		throw new Error(`${res.status}: ${t}`);
	}
	return res.json();
}

function LoginScreen({ navigation }: any) {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	return (
		<SafeAreaView style={{ padding: 16 }}>
			<Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 16 }}>HealthShare Login</Text>
			<TextInput placeholder="Email" autoCapitalize='none' value={email} onChangeText={setEmail} style={{ borderWidth: 1, padding: 8, marginBottom: 12 }} />
			<TextInput placeholder="Password" secureTextEntry value={password} onChangeText={setPassword} style={{ borderWidth: 1, padding: 8, marginBottom: 12 }} />
			{error ? <Text style={{ color: 'red' }}>{error}</Text> : null}
			<Button title="Login" onPress={async () => {
				try {
					const data = await api('/auth/login', 'POST', { email, password });
					await SecureStore.setItemAsync('token', data.access_token);
					navigation.replace('Home');
				} catch (e: any) {
					setError(e.message);
				}
			}} />
		</SafeAreaView>
	);
}

function ListScreen({ token, endpoint, title }: { token: string; endpoint: string; title: string }) {
	const [items, setItems] = useState<any[]>([]);
	const [error, setError] = useState('');
	useEffect(() => {
		(async () => {
			try {
				const data = await api(endpoint, 'GET', undefined, token);
				setItems(data);
			} catch (e: any) {
				setError(e.message);
			}
		})();
	}, [endpoint, token]);
	return (
		<SafeAreaView style={{ flex: 1 }}>
			<Text style={{ fontSize: 20, fontWeight: '600', margin: 12 }}>{title}</Text>
			{error ? <Text style={{ color: 'red', marginHorizontal: 12 }}>{error}</Text> : null}
			<FlatList data={items} keyExtractor={(it) => `${it.id}`} renderItem={({ item }) => (
				<View style={{ padding: 12, borderBottomWidth: 1 }}>
					<Text style={{ fontWeight: '600' }}>{item.title || item.name || item.medication_name}</Text>
					<Text numberOfLines={2}>
						{item.content || item.result || item.instructions}
					</Text>
					<Text style={{ color: '#666' }}>Created: {new Date(item.created_at).toLocaleString()}</Text>
				</View>
			)} />
		</SafeAreaView>
	);
}

function HomeScreen({ navigation }: any) {
	const [token, setToken] = useState<string | null>(null);
	useEffect(() => {
		SecureStore.getItemAsync('token').then(setToken);
	}, []);
	if (!token) {
		return (
			<SafeAreaView style={{ padding: 16 }}>
				<Text>Loading...</Text>
			</SafeAreaView>
		);
	}
	return (
		<SafeAreaView style={{ flex: 1 }}>
			<View style={{ flexDirection: 'row', justifyContent: 'space-around', padding: 12 }}>
				<TouchableOpacity onPress={() => navigation.navigate('List', { token, endpoint: '/records', title: 'Records' })}><Text>Records</Text></TouchableOpacity>
				<TouchableOpacity onPress={() => navigation.navigate('List', { token, endpoint: '/tests', title: 'Tests' })}><Text>Tests</Text></TouchableOpacity>
				<TouchableOpacity onPress={() => navigation.navigate('List', { token, endpoint: '/prescriptions', title: 'Prescriptions' })}><Text>Prescriptions</Text></TouchableOpacity>
				<TouchableOpacity onPress={() => navigation.navigate('Grants', { token })}><Text>Grants</Text></TouchableOpacity>
			</View>
		</SafeAreaView>
	);
}

function GrantsScreen({ route }: any) {
	const { token } = route.params as { token: string };
	const [grants, setGrants] = useState<any[]>([]);
	const [error, setError] = useState('');
	useEffect(() => {
		(async () => {
			try {
				const data = await api('/grants/mine', 'GET', undefined, token);
				setGrants(data);
			} catch (e: any) {
				setError(e.message);
			}
		})();
	}, [token]);
	return (
		<SafeAreaView style={{ flex: 1 }}>
			<Text style={{ fontSize: 20, fontWeight: '600', margin: 12 }}>My Grants</Text>
			{error ? <Text style={{ color: 'red', marginHorizontal: 12 }}>{error}</Text> : null}
			<FlatList data={grants} keyExtractor={(g) => `${g.id}`} renderItem={({ item }) => (
				<View style={{ padding: 12, borderBottomWidth: 1 }}>
					<Text>To user: {item.granted_to_user_id}</Text>
					<Text>Scopes: {item.scopes.join(', ')}</Text>
					<Text>Expires: {item.expires_at ? new Date(item.expires_at).toLocaleString() : 'none'}</Text>
				</View>
			)} />
		</SafeAreaView>
	);
}

const Stack = createNativeStackNavigator();

export default function App() {
	return (
		<NavigationContainer>
			<Stack.Navigator>
				<Stack.Screen name="Login" component={LoginScreen} />
				<Stack.Screen name="Home" component={HomeScreen} />
				<Stack.Screen name="List" component={({ route }: any) => (
					<ListScreen token={route.params.token} endpoint={route.params.endpoint} title={route.params.title} />
				)} />
				<Stack.Screen name="Grants" component={GrantsScreen} />
			</Stack.Navigator>
		</NavigationContainer>
	);
}