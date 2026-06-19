import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SIEMBRA CAJA - ERP", layout="wide", page_icon="🌱")

# --- SIMULACIÓN DE BASE DE DATOS EN MEMORIA ---
# En producción, esto se conectaría a una base de datos real (SQLite, PostgreSQL, etc.)
if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame([
        {"ID": 1, "Nombre": "Socio Juan Pérez", "Teléfono": "099123456", "Cumpleaños": "15/06", "Estado": "Activo", "Saldo": 1500},
        {"ID": 2, "Nombre": "Socio María Rodríguez", "Teléfono": "098765432", "Cumpleaños": "22/11", "Estado": "Activo", "Saldo": 0}
    ])

if "productos" not in st.session_state:
    st.session_state.productos = pd.DataFrame([
        {"Código": "P001", "Variedad": "24 K", "Familia": "Flores", "Stock": 120.5},
        {"Código": "P002", "Variedad": "Gorilla Glue", "Familia": "Flores", "Stock": 45.0}
    ])

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {"Fecha": "2026-06-18", "Recibo": "V-001", "Cliente": "Socio Juan Pérez", "Variedad": "24 K", "Gramos": 5, "Precio/g": 300, "Total": 1500, "Condición": "Debe"}
    ])

# --- MENÚ DE NAVEGACIÓN ---
st.sidebar.title("🌱 SIEMBRA CAJA")
st.sidebar.write("Sistema de Gestión Comercial")
menu = st.sidebar.radio("Ir a:", ["📊 Dashboard", "👥 Clientes", "🌿 Productos / Stock", "🛍️ Registrar Venta", "💰 Caja y Finanzas"])

# ==========================================
# --- MODULO 1: DASHBOARD ---
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Panel de Control General")
    st.write("Resumen automatizado en tiempo real.")
    
    # Indicadores Clave (KPIs)
    total_ventas = st.session_state.ventas["Total"].sum()
    deuda_total = st.session_state.clientes["Saldo"].sum()
    total_clientes = len(st.session_state.clientes)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales ($)", f"${total_ventas:,.2f}")
    col2.metric("Deuda Total de Socios ($)", f"${deuda_total:,.2f}", delta="- Activa", delta_color="inverse")
    col3.metric("Socios Registrados", total_clientes)
    
    st.subheader("Últimas Transacciones")
    st.dataframe(st.session_state.ventas.tail(5), use_container_width=True)

# ==========================================
# --- MODULO 2: CLIENTES ---
# ==========================================
elif menu == "👥 Clientes":
    st.title("👥 Base de Datos de Clientes / Socios")
    
    # Formulario para nuevo cliente
    with st.expander("➕ Registrar Nuevo Socio"):
        with st.form("nuevo_cliente"):
            nombre = st.text_input("Nombre Completo")
            tel = st.text_input("Teléfono")
            cumple = st.text_input("Cumpleaños (DD/MM)")
            enviar = st.form_submit_button("Guardar Socio")
            if enviar and nombre:
                nuevo_id = len(st.session_state.clientes) + 1
                nueva_fila = {"ID": nuevo_id, "Nombre": nombre, "Teléfono": tel, "Cumpleaños": cumple, "Estado": "Activo", "Saldo": 0}
                st.session_state.clientes = pd.concat([st.session_state.clientes, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.success("Socio guardado correctamente.")
                st.rerun()

    st.dataframe(st.session_state.clientes, use_container_width=True)

# ==========================================
# --- MODULO 3: PRODUCTOS Y STOCK ---
# ==========================================
elif menu == "🌿 Productos / Stock":
    st.title("🌿 Gestión de Variedades e Inventario")
    
    # 1. Alerta de stock bajo
    stock_critico = st.session_state.productos[st.session_state.productos["Stock"] < 50]
    if not stock_critico.empty:
        st.warning(f"⚠️ ¡Atención! Hay {len(stock_critico)} variedades con stock crítico (menos de 50g).")
        
    # 2. Mostrar la tabla actual
    st.dataframe(st.session_state.productos, use_container_width=True)

    # 3. Formulario para Ajuste Manual de Stock
    st.markdown("---")
    st.subheader("🔄 Ingreso / Egreso Manual de Stock")
    st.write("Registra nuevas cosechas, compras o ajusta el stock por recuentos.")
    
    with st.form("modificar_stock"):
        col1, col2 = st.columns(2)
        
        with col1:
            var_seleccionada = st.selectbox("Seleccionar Variedad", st.session_state.productos["Variedad"].tolist())
            tipo_mov = st.radio("Tipo de Movimiento", ["Entrada (+) - Ej: Cosecha/Compra", "Salida (-) - Ej: Merma/Ajuste"])
        
        with col2:
            cantidad = st.number_input("Cantidad (Gramos)", min_value=0.1, step=1.0)
            concepto = st.text_input("Concepto / Observación")
            
        btn_actualizar = st.form_submit_button("Actualizar Inventario")
        
        if btn_actualizar:
            # Encontrar la fila exacta de esa variedad
            idx = st.session_state.productos.index[st.session_state.productos['Variedad'] == var_seleccionada].tolist()[0]
            
            # Aplicar la suma o la resta según lo elegido
            if "Entrada" in tipo_mov:
                st.session_state.productos.at[idx, "Stock"] += cantidad
                st.success(f"✅ Se sumaron {cantidad}g de {var_seleccionada}. Motivo: {concepto}")
            else:
                st.session_state.productos.at[idx, "Stock"] -= cantidad
                st.success(f"✅ Se restaron {cantidad}g de {var_seleccionada}. Motivo: {concepto}")
                
            # Recargar la página para que la tabla muestre el nuevo stock
            st.rerun()

# ==========================================
# --- MODULO 4: REGISTRAR VENTA ---
# ==========================================
elif menu == "🛍️ Registrar Venta":
    st.title("🛍️ Nueva Transacción de Venta")
    
    with st.form("formulario_venta"):
        cliente_sel = st.selectbox("Seleccionar Socio", st.session_state.clientes["Nombre"].tolist())
        producto_sel = st.selectbox("Seleccionar Variedad", st.session_state.productos["Variedad"].tolist())
        gramos = st.number_input("Cantidad (Gramos)", min_value=0.1, step=0.1)
        precio = st.number_input("Precio por Gramo ($)", min_value=1, step=10)
        condicion = st.radio("Condición de Pago", ["Paga en el momento", "Debe"])
        
        procesar = st.form_submit_button("Procesar Venta 🚀")
        
        if procesar:
            total = gramos * precio
            nro_recibo = f"V-{len(st.session_state.ventas) + 1:03d}"
            nueva_venta = {
                "Fecha": str(datetime.date.today()),
                "Recibo": nro_recibo,
                "Cliente": cliente_sel,
                "Variedad": producto_sel,
                "Gramos": gramos,
                "Precio/g": precio,
                "Total": total,
                "Condición": condicion
            }
            
            # 1. Registrar Venta
            st.session_state.ventas = pd.concat([st.session_state.ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
            
            # 2. Descontar Stock automáticamente
            idx_prod = st.session_state.productos.index[st.session_state.productos["Variedad"] == producto_sel].tolist()[0]
            st.session_state.productos.at[idx_prod, "Stock"] -= gramos
            
            # 3. Si debe, sumar al saldo de deuda del cliente
            if condicion == "Debe":
                idx_cli = st.session_state.clientes.index[st.session_state.clientes["Nombre"] == cliente_sel].tolist()[0]
                st.session_state.clientes.at[idx_cli, "Saldo"] += total
                
            st.success(f"Venta procesada con éxito. Recibo: {nro_recibo}. Total: ${total:,.2f}")

# ==========================================
# --- MODULO 5: CAJA Y FINANZAS ---
# ==========================================
elif menu == "💰 Caja y Finanzas":
    st.title("💰 Informes Financieros y Arqueo de Caja")
    
    tab1, tab2 = st.tabs(["Arqueo Diario", "Estado de Resultados"])
    
    with tab1:
        st.subheader("Control del Efectivo en Caja")
        st.write("Estructura basada en la denominación de billetes de tu pestaña 'Arqueo Caja'.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            b_2000 = st.number_input("Billetes de $2000", min_value=0, step=1)
            b_1000 = st.number_input("Billetes de $1000", min_value=0, step=1)
            b_500 = st.number_input("Billetes de $500", min_value=0, step=1)
        with col2:
            b_200 = st.number_input("Billetes de $200", min_value=0, step=1)
            b_100 = st.number_input("Billetes de $100", min_value=0, step=1)
            b_50 = st.number_input("Billetes de $50", min_value=0, step=1)
        with col3:
            b_20 = st.number_input("Billetes de $20", min_value=0, step=1)
            m_10 = st.number_input("Monedas de $10", min_value=0, step=1)
            m_otros = st.number_input("Otras monedas", min_value=0, step=1)
        
        total_arqueo = (b_2000*2000) + (b_1000*1000) + (b_500*500) + (b_200*200) + (b_100*100) + (b_50*50) + (b_20*20) + (m_10*10) + m_otros
        st.info(f"Total Contado en Caja (Efectivo Físico): **${total_arqueo:,.2f}**")
        
    with tab2:
        st.subheader("Estado de Resultados Mensual")
        # Sumamos el total de ventas que hayan sido en efectivo (no "Debe")
        ventas_efectivo = st.session_state.ventas[st.session_state.ventas["Condición"] == "Paga en el momento"]["Total"].sum()
        
        st.markdown("""
        | Concepto | Monto |
        | :--- | :--- |
        | **(+) Ingresos por Ventas (Efectivo)** |  ${:,.2f} |
        | **(-) Costo de Mercadería** | $0.00 |
        | **(-) Gastos Operativos** | $0.00 |
        | --- | --- |
        | **(=) Resultado Neto de Caja** | **${:,.2f}** |
        """.format(ventas_efectivo, ventas_efectivo))