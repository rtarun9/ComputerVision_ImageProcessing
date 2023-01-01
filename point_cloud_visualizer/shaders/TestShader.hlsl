struct VSInput
{
    float2 position : POSITION;
    float2 textureCoord : TEXTURECOORD;
};

struct VSOutput
{
    float4 position : SV_Position;
    float2 textureCoord : TEX_COORD;
};

cbuffer sceneBuffer : register(b0)
{
    row_major matrix viewMatrix;
    row_major matrix viewProjectionMatrix;
}

VSOutput VsMain(VSInput input)
{
    VSOutput output;
    output.position = mul(float4(input.position.xy, 1.0f, 1.0f), viewProjectionMatrix);
    output.textureCoord = input.textureCoord;

    return output;
}

Texture2D<float4> tex : register(t0);
Texture2D<float> depthTexture : register(t1);

SamplerState smp : register(s0);

struct PSOutput
{
    float4 color : SV_Target;
    float depth : SV_Depth;
};

PSOutput PsMain(VSOutput input)
{
    PSOutput output;
    output.color = tex.Sample(smp, input.textureCoord);
    output.depth = 1.0 - depthTexture.Sample(smp, input.textureCoord).x;

    return output;
}