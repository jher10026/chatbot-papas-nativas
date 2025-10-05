"""
Script para analizar las métricas del chatbot de papas nativas
Genera reportes y visualizaciones del uso del chatbot
"""

import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict

def leer_logs(archivo='chatbot_analytics.log'):
    """Lee y parsea el archivo de logs"""
    eventos = []
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                try:
                    # Extraer el JSON de cada línea
                    json_str = linea.split(' - ', 1)[1].strip()
                    evento = json.loads(json_str)
                    evento['timestamp'] = datetime.fromisoformat(evento['timestamp'])
                    eventos.append(evento)
                except (IndexError, json.JSONDecodeError, KeyError):
                    continue
    except FileNotFoundError:
        print(f"Archivo {archivo} no encontrado")
    
    return eventos

def generar_estadisticas_generales(eventos):
    """Genera estadísticas generales del chatbot"""
    print("=" * 60)
    print("ESTADÍSTICAS GENERALES DEL CHATBOT")
    print("=" * 60)
    
    if not eventos:
        print("No hay datos disponibles")
        return
    
    # Total de interacciones
    total = len(eventos)
    print(f"\n📊 Total de interacciones: {total}")
    
    # Usuarios únicos
    usuarios = set(e['usuario'] for e in eventos)
    print(f"👥 Usuarios únicos: {len(usuarios)}")
    
    # Promedio de interacciones por usuario
    promedio = total / len(usuarios) if usuarios else 0
    print(f"📈 Promedio de interacciones por usuario: {promedio:.2f}")
    
    # Distribución de eventos
    tipos_evento = Counter(e['evento'] for e in eventos)
    print(f"\n📋 Distribución de eventos:")
    for evento, cantidad in tipos_evento.most_common():
        porcentaje = (cantidad / total) * 100
        print(f"   • {evento}: {cantidad} ({porcentaje:.1f}%)")
    
    # Periodo de análisis
    fechas = [e['timestamp'] for e in eventos]
    if fechas:
        fecha_inicio = min(fechas)
        fecha_fin = max(fechas)
        dias = (fecha_fin - fecha_inicio).days + 1
        print(f"\n📅 Periodo analizado: {fecha_inicio.date()} a {fecha_fin.date()} ({dias} días)")

def analizar_intents(eventos):
    """Analiza los intents más consultados"""
    print("\n" + "=" * 60)
    print("INTENTS MÁS CONSULTADOS")
    print("=" * 60)
    
    interacciones = [e for e in eventos if e['evento'] == 'interaccion']
    
    if not interacciones:
        print("No hay datos de intents")
        return
    
    intents = Counter(e['intent'] for e in interacciones)
    
    print(f"\n🎯 Top 10 intents:")
    for intent, cantidad in intents.most_common(10):
        porcentaje = (cantidad / len(interacciones)) * 100
        print(f"   {cantidad:3d} ({porcentaje:5.1f}%) - {intent}")
    
    # Confianza promedio
    confianzas = [e['confianza'] for e in interacciones if 'confianza' in e]
    if confianzas:
        promedio_confianza = sum(confianzas) / len(confianzas)
        print(f"\n🎲 Confianza promedio: {promedio_confianza:.2%}")
        
        # Intents con baja confianza
        bajas = [e for e in interacciones if e.get('confianza', 1) < 0.7]
        if bajas:
            print(f"⚠️  Interacciones con baja confianza (<70%): {len(bajas)}")

def analizar_variedades(eventos):
    """Analiza las variedades más consultadas"""
    print("\n" + "=" * 60)
    print("VARIEDADES MÁS CONSULTADAS")
    print("=" * 60)
    
    consultas = [e for e in eventos if e['evento'] == 'consulta_variedad']
    
    if not consultas:
        print("No hay consultas de variedades registradas")
        return
    
    variedades = Counter(e['variedad'] for e in consultas)
    
    print(f"\n🥔 Top variedades consultadas:")
    for variedad, cantidad in variedades.most_common():
        porcentaje = (cantidad / len(consultas)) * 100
        print(f"   {cantidad:3d} ({porcentaje:5.1f}%) - {variedad}")

def analizar_busquedas_recetas(eventos):
    """Analiza las búsquedas de recetas"""
    print("\n" + "=" * 60)
    print("BÚSQUEDAS DE RECETAS")
    print("=" * 60)
    
    busquedas = [e for e in eventos if e['evento'] == 'busqueda_receta']
    
    if not busquedas:
        print("No hay búsquedas de recetas registradas")
        return
    
    print(f"\n👨‍🍳 Total de búsquedas de recetas: {len(busquedas)}")

def analizar_patrones_temporales(eventos):
    """Analiza patrones de uso por hora y día"""
    print("\n" + "=" * 60)
    print("PATRONES TEMPORALES DE USO")
    print("=" * 60)
    
    if not eventos:
        print("No hay datos disponibles")
        return
    
    # Por hora del día
    horas = defaultdict(int)
    for e in eventos:
        hora = e['timestamp'].hour
        horas[hora] += 1
    
    print(f"\n⏰ Distribución por hora:")
    for hora in sorted(horas.keys()):
        barra = '█' * (horas[hora] // 2)
        print(f"   {hora:02d}:00 - {barra} ({horas[hora]})")
    
    # Por día de la semana
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias = defaultdict(int)
    for e in eventos:
        dia = e['timestamp'].weekday()
        dias[dia] += 1
    
    print(f"\n📅 Distribución por día de la semana:")
    for dia_num in sorted(dias.keys()):
        nombre_dia = dias_semana[dia_num]
        barra = '█' * (dias[dia_num] // 2)
        print(f"   {nombre_dia:10s} - {barra} ({dias[dia_num]})")

def generar_reporte_completo():
    """Genera un reporte completo del chatbot"""
    eventos = leer_logs()
    
    if not eventos:
        print("No hay datos para generar el reporte")
        return
    
    print("\n" + "=" * 60)
    print("REPORTE COMPLETO - CHATBOT PAPAS NATIVAS DEL PERÚ")
    print("=" * 60)
    print(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    generar_estadisticas_generales(eventos)
    analizar_intents(eventos)
    analizar_variedades(eventos)
    analizar_busquedas_recetas(eventos)
    analizar_patrones_temporales(eventos)

def estadisticas_tiempo_real():
    """Muestra estadísticas en tiempo real (últimas 24 horas)"""
    eventos = leer_logs()
    
    if not eventos:
        print("No hay datos disponibles")
        return
    
    # Filtrar últimas 24 horas
    hace_24h = datetime.now() - timedelta(hours=24)
    eventos_recientes = [e for e in eventos if e['timestamp'] >= hace_24h]
    
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS ÚLTIMAS 24 HORAS")
    print("=" * 60)
    
    print(f"\n📊 Interacciones últimas 24h: {len(eventos_recientes)}")
    
    if eventos_recientes:
        usuarios_24h = set(e['usuario'] for e in eventos_recientes)
        print(f"👥 Usuarios activos: {len(usuarios_24h)}")
        
        # Intents más consultados
        interacciones = [e for e in eventos_recientes if e['evento'] == 'interaccion']
        if interacciones:
            intents = Counter(e['intent'] for e in interacciones)
            print(f"\n🎯 Top 5 intents (24h):")
            for intent, cantidad in intents.most_common(5):
                print(f"   • {intent}: {cantidad}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "completo":
            generar_reporte_completo()
        elif comando == "real-time":
            estadisticas_tiempo_real()
        else:
            print("Comandos disponibles:")
            print("  python analytics.py completo    - Genera reporte completo")
            print("  python analytics.py real-time   - Estadísticas últimas 24h")
    else:
        # Por defecto, mostrar reporte completo
        generar_reporte_completo()