#include "Pch.hpp"

#include "Engine.hpp"

#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

#define TINYOBJLOADER_IMPLEMENTATION
#include <tiny_obj_loader.h>

using namespace math;

Engine::Engine(const std::string_view windowTitle) : pcviz::Application(windowTitle) {}

void Engine::loadContent()
{
    m_wrapSampler = createSampler(pcviz::SamplerCreationDesc{
        .filter = D3D11_FILTER_MIN_MAG_MIP_POINT,
        .addressMode = D3D11_TEXTURE_ADDRESS_WRAP,
    });

    m_pipeline = createGraphicsPipeline(pcviz::GraphicsPipelineCreationDesc{
        .vertexShaderPath = L"shaders/TestShader.hlsl",
        .pixelShaderPath = L"shaders/TestShader.hlsl",
        .inputLayoutElements =
            {
                pcviz::InputLayoutElementDesc{.semanticName = "Position", .format = DXGI_FORMAT_R32G32B32_FLOAT, .inputClassification = D3D11_INPUT_PER_VERTEX_DATA},
                pcviz::InputLayoutElementDesc{.semanticName = "TextureCoord", .format = DXGI_FORMAT_R32G32_FLOAT, .inputClassification = D3D11_INPUT_PER_VERTEX_DATA},
            },
        .primitiveTopology = D3D11_PRIMITIVE_TOPOLOGY::D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST,
        .vertexSize = sizeof(pcviz::VertexPosTexCoord),
    });

    m_sceneBuffer = createConstantBuffer<pcviz::SceneBuffer>();

    m_depthTexture = createDepthTexture();

    m_renderTarget = createRenderTarget(m_windowWidth, m_windowHeight, DXGI_FORMAT_R8G8B8A8_UNORM_SRGB);

    m_texture = createTexture(L"../data/stereo/left.jpg");
    m_depthMap = createTexture(L"../data/stereo/depth_map.jpg");
    m_disparityMap = createTexture(L"../data/stereo/disparity_map.jpg");

    // hardcoding texel count for depth map :(.
    std::vector<pcviz::VertexPosTexCoord> vertexData{};
    
    m_depthMapTexelCount = 400 * 879;

    // Load the cube obj model.

    tinyobj::attrib_t attrib;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;

    std::string warn;
    std::string err;

    bool ret = tinyobj::LoadObj(&attrib, &shapes, &materials, &warn, &err, "assets/cube.obj");

    // Loop over shapes
    for (size_t s = 0; s < shapes.size(); s++)
    {
        // Loop over faces(polygon)
        size_t index_offset = 0;
        for (size_t f = 0; f < shapes[s].mesh.num_face_vertices.size(); f++)
        {
            size_t fv = size_t(shapes[s].mesh.num_face_vertices[f]);

            // Loop over vertices in the face.
            for (size_t v = 0; v < fv; v++)
            {
                // access to vertex
                tinyobj::index_t idx = shapes[s].mesh.indices[index_offset + v];

                tinyobj::real_t vx = attrib.vertices[3 * size_t(idx.vertex_index) + 0];
                tinyobj::real_t vy = attrib.vertices[3 * size_t(idx.vertex_index) + 1];
                tinyobj::real_t vz = attrib.vertices[3 * size_t(idx.vertex_index) + 2];

                tinyobj::real_t tx = attrib.texcoords[2 * size_t(idx.texcoord_index) + 0];
                tinyobj::real_t ty = 1.0f - attrib.texcoords[2 * size_t(idx.texcoord_index) + 1];

                vertexData.emplace_back(pcviz::VertexPosTexCoord{.position = {vx, vy, vz}, .texCoord{tx, ty}});
            }
            index_offset += fv;

            // per-face material
            shapes[s].mesh.material_ids[f];
        }
    }

    m_vertexBuffer = createBuffer<pcviz::VertexPosTexCoord>(pcviz::BufferCreationDesc{.usage = D3D11_USAGE_IMMUTABLE, .bindFlags = D3D11_BIND_VERTEX_BUFFER}, vertexData);
    m_verticesCount = vertexData.size();
}

void Engine::update(const float deltaTime)
{
    m_camera.update(deltaTime);

    const math::XMMATRIX modelMatrix = math::XMMatrixScaling(0.01f, 0.01f, 0.01f);
    const math::XMMATRIX viewMatrix = m_camera.getLookAtMatrix();
    const math::XMMATRIX projectionMatrix = math::XMMatrixPerspectiveFovLH(math::XMConvertToRadians(45.0f), m_windowWidth / static_cast<float>(m_windowHeight), 0.1f, 250.0f);

    m_sceneBuffer.data.modelMatrix = modelMatrix;
    m_sceneBuffer.data.viewMatrix = viewMatrix;
    m_sceneBuffer.data.viewProjectionMatrix = viewMatrix * projectionMatrix;

    updateConstantBuffer(m_sceneBuffer);
}

void Engine::render()
{
    // Start the Dear ImGui frame
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplSDL2_NewFrame();
    ImGui::NewFrame();

    static std::array<float, 4> clearColor{0.0f, 0.0f, 0.0f, 1.0f};

    ImGui::Begin("Scene menu");
    ImGui::SliderFloat("camera mvmt speed", &m_camera.m_movementSpeed, 0.1f, 50.0f);
    ImGui::SliderFloat("camera rotation speed", &m_camera.m_rotationSpeed, 0.1f, 3.0f);
    ImGui::SliderFloat("layer count", &m_sceneBuffer.data.layerCount, 0.0f, 20000.5f);
    ImGui::SliderInt("image select", &m_sceneBuffer.data.imageSelect, 0, 2);
    ImGui::ColorEdit3("bg color", clearColor.data());

    ImGui::End();

    auto& ctx = m_deviceContext;


    ctx->ClearDepthStencilView(m_depthTexture.dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 1u);

    ctx->ClearRenderTargetView(m_renderTargetView.Get(), clearColor.data());

    const float mask[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    // ctx->OMSetBlendState(m_blendState.Get(), mask, 0xffffffff);

    // Render the Geometry pass
    ctx->OMSetRenderTargets(1u, m_renderTargetView.GetAddressOf(), m_depthTexture.dsv.Get());
    ctx->RSSetViewports(1u, &m_viewport);

    bindPipeline(m_pipeline);

    constexpr uint32_t stride = sizeof(pcviz::VertexPosTexCoord);
    constexpr uint32_t offset = 0u;

    ctx->IASetVertexBuffers(0u, 1u, m_vertexBuffer.GetAddressOf(), &stride, &offset);

    ctx->VSSetConstantBuffers(0u, 1u, m_sceneBuffer.buffer.GetAddressOf());
    ctx->VSSetSamplers(0u, 1u, m_wrapSampler.GetAddressOf());
    ctx->VSSetShaderResources(0u, 1u, m_depthMap.GetAddressOf());

    ctx->PSSetConstantBuffers(0u, 1u, m_sceneBuffer.buffer.GetAddressOf());
    ctx->PSSetSamplers(0u, 1u, m_wrapSampler.GetAddressOf());
    ctx->PSSetShaderResources(0u, 1u, m_disparityMap.GetAddressOf());
    ctx->PSSetShaderResources(1u, 1u, m_texture.GetAddressOf());
    ctx->PSSetShaderResources(2u, 1u, m_depthMap.GetAddressOf());

    ctx->DrawInstanced(m_verticesCount, m_depthMapTexelCount, 0u,  0u);

    ImGui::Render();
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    throwIfFailed(m_swapchain->Present(1u, 0u));
}
