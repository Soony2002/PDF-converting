import streamlit as st
import plotly.express as px


def style_chart(fig):

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        title_x=0.3
    )

    fig.update_traces(
        marker=dict(line=dict(width=1, color="white"))
    )

    return fig


def chart_distribution(df):

    fig = px.histogram(
        df,
        x="Final",
        nbins=20,
        title="Phân bố điểm tổng",
        color_discrete_sequence=["#3fa7ff"]
    )

    fig = style_chart(fig)

    fig.update_traces(
        hovertemplate="Điểm: %{x}<br>Số lượng: %{y}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)


def chart_average_class(df):

    avg = df.groupby("Class")["Final"].mean().reset_index()

    fig = px.bar(
        avg,
        x="Class",
        y="Final",
        title="Điểm trung bình theo lớp",
        color="Final",
        color_continuous_scale="Blues"
    )

    fig = style_chart(fig)

    fig.update_traces(
        hovertemplate="Lớp: %{x}<br>Điểm TB: %{y:.2f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)


def chart_top_students(df):

    top_students = df.sort_values("Final", ascending=False).head(10)

    fig = px.bar(
        top_students,
        x="Name",
        y="Final",
        title="Top 10 sinh viên điểm cao",
        color="Final",
        color_continuous_scale="Viridis"
    )

    fig = style_chart(fig)

    st.plotly_chart(fig, use_container_width=True)


def create_chart(prompt, df):

    prompt = prompt.lower()

    if "phân bố" in prompt:
        chart_distribution(df)

    elif "trung bình" in prompt and "lớp" in prompt:
        chart_average_class(df)

    elif "top" in prompt:
        chart_top_students(df)

    else:
        st.warning("Chưa hiểu yêu cầu. Hãy thử ví dụ phía trên.")